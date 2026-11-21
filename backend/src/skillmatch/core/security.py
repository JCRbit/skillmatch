"""Authentication primitives: trusted identity resolution and token verification.

The API never trusts an identifier supplied by the client. The caller proves *who they are* with
a credential (an ``Authorization: Bearer <token>`` header) that only the server can verify, and
the identity, role and account status are then read from the database.

The credential is a compact JWS signed with HMAC-SHA256 using a secret that only the server knows
(``SKILLMATCH_AUTH_SERVICE_SECRET``). The token carries the subject (``sub``), the role and the
expiry (``exp``); a client cannot forge one, and editing its payload invalidates the signature.

This keeps the authentication boundary trustworthy while the user-facing login flow (password
hashing + session persistence) is still out of scope: the service issues the token after its own
login step, and every request must present it. Swapping in an OIDC provider later only means
replacing :func:`verify_token`; the rest of the API does not change.

Verification returns the token *claims*. Resolving those claims to a live user record is the job
of :func:`skillmatch.api.deps.get_current_user`, which is what makes the role and the account
status authoritative in the database instead of in the credential.

Secrets are read from settings and must never be committed.
"""

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any, Final

from skillmatch.core.config import Settings

SIGNING_ALGORITHM: Final = "HS256"
"""Algorithm used to sign and verify access tokens."""


class InvalidTokenError(Exception):
    """The presented credential is malformed, expired or was not issued by a trusted party."""


@dataclass(frozen=True, slots=True)
class TokenClaims:
    """Verified content of an access token.

    Attributes:
        subject: Identifier of the user the token was issued for.
        role: Role asserted by the issuer, as its raw string value. It is *not* used for
            authorization: the database record is authoritative. It is kept for traceability and
            for services that only need the claim.
        expires_at: Unix timestamp after which the token is no longer valid.
    """

    subject: str
    role: str | None
    expires_at: int


def _b64url_encode(data: bytes) -> str:
    """Encode bytes as unpadded base64url, as required by JOSE."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    """Decode an unpadded base64url segment.

    Raises:
        InvalidTokenError: The segment is not valid base64url.
    """
    padding = "=" * (-len(segment) % 4)
    try:
        return base64.urlsafe_b64decode(segment + padding)
    except (ValueError, TypeError) as exc:
        raise InvalidTokenError("El token no está correctamente codificado.") from exc


def _encode_segment(payload: dict[str, Any]) -> str:
    """Serialize a JOSE header or claim set to its base64url representation."""
    return _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )


def _sign(signing_input: bytes, secret: str) -> bytes:
    """Return the HMAC-SHA256 signature of ``signing_input``."""
    return hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()


def create_service_token(
    *,
    subject: str,
    role: str,
    secret: str,
    expires_in: int = 900,
    now: int | None = None,
) -> str:
    """Issue an access token signed by this service.

    Args:
        subject: Identifier of the user the token is issued to.
        role: Role the user holds, as its string value (e.g. ``UserRole.ADMIN.value``).
        secret: Signing secret; the same value must be configured for verification.
        expires_in: Lifetime of the token in seconds.
        now: Current Unix timestamp, injectable for deterministic tests.

    Returns:
        The compact JWS string to send as ``Authorization: Bearer <token>``.
    """
    issued_at = int(time.time()) if now is None else now
    header = {"alg": SIGNING_ALGORITHM, "typ": "JWT"}
    claims = {
        "sub": subject,
        "role": role,
        "iat": issued_at,
        "exp": issued_at + expires_in,
    }
    signing_input = f"{_encode_segment(header)}.{_encode_segment(claims)}".encode("ascii")
    signature = _b64url_encode(_sign(signing_input, secret))
    return f"{signing_input.decode('ascii')}.{signature}"


def _verify_service_token(token: str, secret: str, now: int | None = None) -> TokenClaims:
    """Verify a token signed by this service with HMAC-SHA256."""
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidTokenError("El token no tiene el formato esperado.")

    header_segment, claims_segment, signature_segment = parts
    try:
        signing_input = f"{header_segment}.{claims_segment}".encode("ascii")
    except UnicodeEncodeError as exc:
        raise InvalidTokenError("El token no está correctamente codificado.") from exc

    expected_signature = _sign(signing_input, secret)
    provided_signature = _b64url_decode(signature_segment)
    if not hmac.compare_digest(expected_signature, provided_signature):
        raise InvalidTokenError("La firma del token no es válida.")

    try:
        header = json.loads(_b64url_decode(header_segment))
    except (json.JSONDecodeError, InvalidTokenError) as exc:
        raise InvalidTokenError("La cabecera del token no es válida.") from exc
    if not isinstance(header, dict) or header.get("alg") != SIGNING_ALGORITHM:
        raise InvalidTokenError("El algoritmo del token no está permitido.")

    try:
        claims = json.loads(_b64url_decode(claims_segment))
    except (json.JSONDecodeError, InvalidTokenError) as exc:
        raise InvalidTokenError("El contenido del token no es válido.") from exc
    if not isinstance(claims, dict):
        raise InvalidTokenError("El contenido del token no es válido.")

    return _claims_from_payload(claims, now=now)


def _role_claim(raw_role: object) -> str | None:
    """Return the ``role`` claim as a plain string, ignoring values that are not text."""
    return raw_role if isinstance(raw_role, str) and raw_role.strip() else None


def _claims_from_payload(payload: dict[str, Any], *, now: int | None = None) -> TokenClaims:
    """Validate the standard claims and build :class:`TokenClaims`."""
    current_time = int(time.time()) if now is None else now

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise InvalidTokenError("El token no identifica a ningún usuario.")

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        raise InvalidTokenError("El token no indica su fecha de expiración.")
    if expires_at <= current_time:
        raise InvalidTokenError("El token ha expirado.")

    return TokenClaims(
        subject=subject,
        role=_role_claim(payload.get("role")),
        expires_at=expires_at,
    )


def verify_token(
    token: str,
    settings: Settings,
    *,
    now: int | None = None,
) -> TokenClaims:
    """Verify an access token signed by this service.

    Args:
        token: Raw credential taken from the ``Authorization`` header.
        settings: Application settings holding the signing secret.
        now: Current Unix timestamp, injectable for deterministic tests.

    Returns:
        The verified claims.

    Raises:
        InvalidTokenError: The token is malformed, forged, expired or unverifiable, or no secret
            is configured (the service fails closed instead of trusting anything).
    """
    secret = settings.auth_service_secret.get_secret_value()
    if not secret:
        raise InvalidTokenError("La autenticación por token no está configurada.")
    return _verify_service_token(token, secret, now=now)
