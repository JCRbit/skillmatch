"""Tests for the token layer used by the authentication boundary (FR-001, NFR-005)."""

import base64
import hashlib
import hmac
import json

import pytest

from skillmatch.core.config import Settings
from skillmatch.core.security import (
    InvalidTokenError,
    _b64url_decode,
    create_service_token,
    verify_token,
)
from skillmatch.modules.identity.models import UserRole

SECRET = "unit-test-secret"  # noqa: S105 - synthetic value
FAR_FUTURE = 9_999_999_999


def _sign(header: str, claims: str, secret: str = SECRET) -> str:
    """Sign a header/claims pair with the real key, to test claim validation on its own."""
    signing_input = f"{header}.{claims}".encode("ascii")
    signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).rstrip(b"=").decode()


def _token_with_claims(
    claims: dict[str, object],
    secret: str = SECRET,
    *,
    include_iat: bool = True,
) -> str:
    """Build a validly signed token carrying the given claims."""
    payload = {"iat": 0, **claims} if include_iat else claims
    header = _segment({"alg": "HS256", "typ": "JWT"})
    claims_segment = _segment(payload)
    return f"{header}.{claims_segment}.{_sign(header, claims_segment, secret)}"


def _settings(secret: str = SECRET) -> Settings:
    return Settings(auth_service_secret=secret)  # type: ignore[arg-type]


def _segment(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def test_valid_token_returns_its_claims() -> None:
    token = create_service_token(
        subject="42",
        role=UserRole.EMPRESA.value,
        secret=SECRET,
        expires_in=60,
        now=1_000,
    )

    claims = verify_token(token, _settings(), now=1_010)

    assert claims.subject == "42"
    assert claims.role == "empresa"
    assert claims.expires_at == 1_060


def test_token_without_role_claim_has_no_role() -> None:
    token = _token_with_claims({"sub": "7", "exp": FAR_FUTURE})

    claims = verify_token(token, _settings(), now=0)

    assert claims.role is None


def test_missing_secret_fails_closed() -> None:
    token = create_service_token(subject="1", role=UserRole.ADMIN.value, secret=SECRET)

    with pytest.raises(InvalidTokenError, match="no está configurada"):
        verify_token(token, _settings(secret=""))


@pytest.mark.parametrize(
    ("token", "message"),
    [
        ("not-a-token", "formato"),
        ("a.b", "formato"),
        ("a.b.c", "codificado"),
    ],
)
def test_malformed_tokens_are_rejected(token: str, message: str) -> None:
    with pytest.raises(InvalidTokenError, match=message):
        verify_token(token, _settings())


def test_unsupported_algorithm_is_rejected() -> None:
    header = _segment({"alg": "none", "typ": "JWT"})
    claims = _segment({"sub": "1", "exp": FAR_FUTURE})

    with pytest.raises(InvalidTokenError, match="algoritmo"):
        verify_token(f"{header}.{claims}.{_sign(header, claims)}", _settings())


def test_tampered_claims_are_rejected() -> None:
    token = create_service_token(subject="1", role=UserRole.TALENTO.value, secret=SECRET)
    header, _claims, signature = token.split(".")
    forged = f"{header}.{_segment({'sub': '1', 'exp': 9_999_999_999, 'role': 'admin'})}.{signature}"

    with pytest.raises(InvalidTokenError, match="firma"):
        verify_token(forged, _settings())


def test_non_json_claims_are_rejected() -> None:
    header = _segment({"alg": "HS256", "typ": "JWT"})
    claims = base64.urlsafe_b64encode(b"not-json").rstrip(b"=").decode()

    with pytest.raises(InvalidTokenError, match="contenido"):
        verify_token(f"{header}.{claims}.{_sign(header, claims)}", _settings())


def test_non_object_claims_are_rejected() -> None:
    header = _segment({"alg": "HS256", "typ": "JWT"})
    claims = _segment(["not", "an", "object"])  # type: ignore[arg-type]

    with pytest.raises(InvalidTokenError, match="contenido"):
        verify_token(f"{header}.{claims}.{_sign(header, claims)}", _settings())


def test_missing_subject_is_rejected() -> None:
    with pytest.raises(InvalidTokenError, match="no identifica"):
        verify_token(_token_with_claims({"sub": "", "exp": FAR_FUTURE}), _settings())


def test_missing_expiry_is_rejected() -> None:
    with pytest.raises(InvalidTokenError, match="expiración"):
        verify_token(_token_with_claims({"sub": "1"}), _settings())


def test_missing_issued_at_is_rejected() -> None:
    token = _token_with_claims(
        {"sub": "1", "exp": FAR_FUTURE},
        include_iat=False,
    )

    with pytest.raises(InvalidTokenError, match="fecha de emisión"):
        verify_token(token, _settings(), now=1_000)


@pytest.mark.parametrize(
    "issued_at",
    [True, False, -1, "1000", None],
)
def test_invalid_issued_at_is_rejected(issued_at: object) -> None:
    token = _token_with_claims(
        {"sub": "1", "iat": issued_at, "exp": FAR_FUTURE},
    )

    with pytest.raises(InvalidTokenError, match="fecha de emisión"):
        verify_token(token, _settings(), now=1_000)


def test_future_issued_at_is_rejected() -> None:
    token = _token_with_claims(
        {"sub": "1", "iat": 1_001, "exp": FAR_FUTURE},
    )

    with pytest.raises(InvalidTokenError, match="emisión futura"):
        verify_token(token, _settings(), now=1_000)


def test_issued_at_equal_to_current_time_is_valid() -> None:
    token = _token_with_claims(
        {"sub": "1", "iat": 1_000, "exp": FAR_FUTURE},
    )

    claims = verify_token(token, _settings(), now=1_000)

    assert claims.subject == "1"


def test_expired_token_is_rejected() -> None:
    token = create_service_token(
        subject="1",
        role=UserRole.TALENTO.value,
        secret=SECRET,
        expires_in=10,
        now=1_000,
    )

    with pytest.raises(InvalidTokenError, match="expirado"):
        verify_token(token, _settings(), now=1_010)


def test_non_text_role_claim_is_ignored() -> None:
    token = _token_with_claims({"sub": "1", "role": 3, "exp": FAR_FUTURE})

    assert verify_token(token, _settings(), now=0).role is None


def test_invalid_base64_signature_is_rejected() -> None:
    header = _segment({"alg": "HS256", "typ": "JWT"})
    claims = _segment({"sub": "1", "exp": FAR_FUTURE})

    with pytest.raises(InvalidTokenError, match="codificado"):
        verify_token(f"{header}.{claims}.!!!not-base64!!!", _settings())


def test_header_that_is_not_json_is_rejected() -> None:
    claims = _segment({"sub": "1", "exp": FAR_FUTURE})
    broken_header = base64.urlsafe_b64encode(b"nope").rstrip(b"=").decode()

    with pytest.raises(InvalidTokenError, match="cabecera"):
        verify_token(f"{broken_header}.{claims}.{_sign(broken_header, claims)}", _settings())


def test_header_with_undecodable_segment_is_rejected() -> None:
    claims = _segment({"sub": "1", "exp": FAR_FUTURE})
    broken_header = "!!!not-base64!!!"

    with pytest.raises(InvalidTokenError, match="cabecera"):
        verify_token(f"{broken_header}.{claims}.{_sign(broken_header, claims)}", _settings())


def test_claims_with_undecodable_segment_are_rejected() -> None:
    header = _segment({"alg": "HS256", "typ": "JWT"})
    broken_claims = "!!!not-base64!!!"

    with pytest.raises(InvalidTokenError, match="contenido"):
        verify_token(f"{header}.{broken_claims}.{_sign(header, broken_claims)}", _settings())


def test_oversized_token_is_rejected() -> None:
    token = "a" * 4097

    with pytest.raises(InvalidTokenError, match="tamaño máximo"):
        verify_token(token, _settings())


@pytest.mark.parametrize(
    "invalid_segment",
    [
        "!!!!",
        "abcd=",
        "abcd ",
        "ab\ncd",
    ],
)
def test_invalid_base64url_characters_in_header_are_rejected(
    invalid_segment: str,
) -> None:
    claims = _segment({"sub": "1", "exp": FAR_FUTURE})
    header = invalid_segment

    with pytest.raises(InvalidTokenError, match="cabecera"):
        verify_token(f"{header}.{claims}.{_sign(header, claims)}", _settings())


@pytest.mark.parametrize("expiry", [True, False])
def test_boolean_expiry_is_rejected(expiry: bool) -> None:
    token = _token_with_claims({"sub": "1", "exp": expiry})

    with pytest.raises(InvalidTokenError, match="expiración"):
        verify_token(token, _settings())


@pytest.mark.parametrize(
    "invalid_segment",
    [
        "!!!!",
        "abcd=",
        "abcd ",
        "ab\ncd",
        "a",
    ],
)
def test_b64url_decode_rejects_invalid_segments(invalid_segment: str) -> None:
    with pytest.raises(InvalidTokenError, match="codificado"):
        _b64url_decode(invalid_segment)
