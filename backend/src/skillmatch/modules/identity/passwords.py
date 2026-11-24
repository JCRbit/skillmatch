"""Password hashing with scrypt, from the Python standard library.

scrypt is a memory-hard key-derivation function and one of the algorithms recommended by the
OWASP Password Storage Cheat Sheet (Argon2id is preferred when a third-party library is
acceptable; this project keeps its dependency set minimal, see ``docs/AUTHENTICATION.md``).

Hashes are stored as self-describing strings in the PHC format::

    $scrypt$ln=17,r=8,p=1$<salt, base64>$<derived key, base64>

so the parameters can be raised later and old hashes are upgraded transparently the next time
their owner logs in (:meth:`PasswordHasher.needs_rehash`).

Hashing is CPU- and memory-bound (about 128 MiB and a few hundred milliseconds with the default
parameters). Use the ``*_async`` methods from request handlers: they run the work in a worker
thread so the event loop keeps serving other requests.
"""

import asyncio
import base64
import binascii
import hashlib
import hmac
import secrets
import unicodedata
from functools import cached_property
from typing import Final

DEFAULT_LOG_N: Final = 17
"""``log2`` of the CPU/memory cost ``N``: 2**17 = 131072 (about 128 MiB with ``r = 8``)."""

DEFAULT_R: Final = 8
"""Block size parameter."""

DEFAULT_P: Final = 1
"""Parallelisation parameter."""

MAX_PASSWORD_LENGTH: Final = 1024
"""Longer inputs are refused outright; the public API accepts far fewer characters."""

_PREFIX: Final = "scrypt"
_MIN_LOG_N: Final = 4
_MAX_LOG_N: Final = 17

_MAX_R: Final = 8
_MAX_P: Final = 4

_MIN_SALT_LENGTH: Final = 16
_MAX_SALT_LENGTH: Final = 64

_MIN_KEY_LENGTH: Final = 16
_MAX_KEY_LENGTH: Final = 64


class PasswordHasher:
    """Hash and verify passwords with scrypt."""

    def __init__(
        self,
        *,
        log_n: int = DEFAULT_LOG_N,
        r: int = DEFAULT_R,
        p: int = DEFAULT_P,
        salt_length: int = 16,
        key_length: int = 32,
    ) -> None:
        """Configure the cost parameters.

        Args:
            log_n: ``log2`` of the cost parameter ``N``. The default follows OWASP's minimum
                (``N = 2**17``, ``r = 8``, ``p = 1``). Lower values are meant for tests only.
            r: Block size.
            p: Parallelisation.
            salt_length: Salt size in bytes (at least 16).
            key_length: Derived key size in bytes (at least 16).

        Raises:
            ValueError: If a parameter is out of its accepted range.
        """
        if not _MIN_LOG_N <= log_n <= _MAX_LOG_N:
            msg = f"log_n must be between {_MIN_LOG_N} and {_MAX_LOG_N}"
            raise ValueError(msg)
        if not 1 <= r <= _MAX_R:
            msg = f"r must be between 1 and {_MAX_R}"
            raise ValueError(msg)
        if not 1 <= p <= _MAX_P:
            msg = f"p must be between 1 and {_MAX_P}"
            raise ValueError(msg)
        if not _MIN_SALT_LENGTH <= salt_length <= _MAX_SALT_LENGTH:
            msg = f"salt_length must be between {_MIN_SALT_LENGTH} and {_MAX_SALT_LENGTH} bytes"
            raise ValueError(msg)
        if not _MIN_KEY_LENGTH <= key_length <= _MAX_KEY_LENGTH:
            msg = f"key_length must be between {_MIN_KEY_LENGTH} and {_MAX_KEY_LENGTH} bytes"
            raise ValueError(msg)
        self._log_n = log_n
        self._r = r
        self._p = p
        self._salt_length = salt_length
        self._key_length = key_length

    @cached_property
    def dummy_hash(self) -> str:
        """A valid hash of a random value, computed once per hasher.

        Verifying a login attempt against it when the account does not exist makes "unknown
        email" take about as long as "wrong password", which limits account enumeration through
        response timing.
        """
        return self.hash(secrets.token_urlsafe(16))

    def hash(self, password: str) -> str:
        """Return the PHC-formatted scrypt hash of ``password`` with a fresh random salt.

        Raises:
            ValueError: If the password is longer than :data:`MAX_PASSWORD_LENGTH`.
        """
        salt = secrets.token_bytes(self._salt_length)
        key = self._derive(password, salt, self._log_n, self._r, self._p, self._key_length)
        return self._encode(self._log_n, self._r, self._p, salt, key)

    def verify(self, password_hash: str, password: str) -> bool:
        """Return whether ``password`` matches ``password_hash``.

        A malformed or unsupported hash, or an over-long password, counts as a mismatch rather
        than an error. The comparison is constant-time.
        """
        parsed = self._decode(password_hash)
        if parsed is None or len(password) > MAX_PASSWORD_LENGTH:
            return False
        log_n, r, p, salt, expected = parsed
        candidate = self._derive(password, salt, log_n, r, p, len(expected))
        return hmac.compare_digest(candidate, expected)

    def needs_rehash(self, password_hash: str) -> bool:
        """Whether ``password_hash`` was made with parameters other than the current ones."""
        parsed = self._decode(password_hash)
        if parsed is None:
            return False
        log_n, r, p, salt, key = parsed
        return (
            (log_n, r, p) != (self._log_n, self._r, self._p)
            or len(salt) != self._salt_length
            or len(key) != self._key_length
        )

    async def hash_async(self, password: str) -> str:
        """Run :meth:`hash` in a worker thread."""
        return await asyncio.to_thread(self.hash, password)

    async def dummy_hash_async(self) -> str:
        """Return the dummy hash without blocking the event loop."""
        return await asyncio.to_thread(lambda: self.dummy_hash)

    async def verify_async(self, password_hash: str, password: str) -> bool:
        """Run :meth:`verify` in a worker thread."""
        return await asyncio.to_thread(self.verify, password_hash, password)

    @staticmethod
    def _derive(password: str, salt: bytes, log_n: int, r: int, p: int, length: int) -> bytes:
        """Derive the key from the NFKC-normalised password."""
        if len(password) > MAX_PASSWORD_LENGTH:
            msg = "password is too long"
            raise ValueError(msg)
        n = 1 << log_n
        return hashlib.scrypt(
            unicodedata.normalize("NFKC", password).encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            maxmem=256 * r * n + (1 << 20),  # an upper bound; OpenSSL refuses above it
            dklen=length,
        )

    @staticmethod
    def _encode(log_n: int, r: int, p: int, salt: bytes, key: bytes) -> str:
        """Serialise parameters, salt and key as a PHC string."""
        salt_text = base64.b64encode(salt).rstrip(b"=").decode("ascii")
        key_text = base64.b64encode(key).rstrip(b"=").decode("ascii")
        return f"${_PREFIX}$ln={log_n},r={r},p={p}${salt_text}${key_text}"

    @staticmethod
    def _decode(password_hash: str) -> tuple[int, int, int, bytes, bytes] | None:
        """Parse a PHC string, or return ``None`` if it is not a valid scrypt hash."""
        parts = password_hash.split("$")
        if len(parts) != 5 or parts[0] != "" or parts[1] != _PREFIX:
            return None
        try:
            params: dict[str, str] = {}
            for item in parts[2].split(","):
                name, value = item.split("=", 1)
                if name in params:
                    return None
                params[name] = value

            if set(params) != {"ln", "r", "p"}:
                return None

            log_n, r, p = int(params["ln"]), int(params["r"]), int(params["p"])
            salt = base64.b64decode(parts[3] + "=" * (-len(parts[3]) % 4), validate=True)
            key = base64.b64decode(parts[4] + "=" * (-len(parts[4]) % 4), validate=True)
        except (KeyError, ValueError, binascii.Error):
            return None
        if (
            not _MIN_LOG_N <= log_n <= _MAX_LOG_N
            or not 1 <= r <= _MAX_R
            or not 1 <= p <= _MAX_P
            or not _MIN_SALT_LENGTH <= len(salt) <= _MAX_SALT_LENGTH
            or not _MIN_KEY_LENGTH <= len(key) <= _MAX_KEY_LENGTH
        ):
            return None
        return log_n, r, p, salt, key
