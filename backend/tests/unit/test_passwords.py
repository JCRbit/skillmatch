import asyncio
import base64

import pytest

from skillmatch.modules.identity.passwords import MAX_PASSWORD_LENGTH, PasswordHasher

PASSPHRASE = "a sufficiently long passphrase"  # noqa: S105 - synthetic value


def _hasher(log_n: int = 4) -> PasswordHasher:
    return PasswordHasher(log_n=log_n)


def test_the_hash_is_a_phc_string_that_never_contains_the_password() -> None:
    password_hash = _hasher().hash(PASSPHRASE)

    assert password_hash.startswith("$scrypt$ln=4,r=8,p=1$")
    assert len(password_hash.split("$")) == 5
    assert PASSPHRASE not in password_hash


def test_the_right_password_verifies_and_a_wrong_one_does_not() -> None:
    hasher = _hasher()
    password_hash = hasher.hash(PASSPHRASE)

    assert hasher.verify(password_hash, PASSPHRASE) is True
    assert hasher.verify(password_hash, "another passphrase!") is False


def test_every_hash_has_its_own_salt() -> None:
    hasher = _hasher()

    assert hasher.hash(PASSPHRASE) != hasher.hash(PASSPHRASE)


def test_equivalent_unicode_forms_of_a_password_match() -> None:
    hasher = _hasher()
    composed = "contrase\u00f1a larga y segura"  # ñ as one code point
    decomposed = "contrasen\u0303a larga y segura"  # n + combining tilde

    assert hasher.verify(hasher.hash(composed), decomposed) is True


@pytest.mark.parametrize(
    "malformed",
    [
        "",
        "plaintext",
        "$argon2id$v=19$m=65536,t=3,p=4$c2FsdA$aGFzaA",
        "$scrypt$ln=4,r=8,p=1$only-three-parts",
        "$scrypt$ln=four,r=8,p=1$c2FsdHNhbHRzYWx0c2FsdA$a2V5",
        "$scrypt$ln=99,r=8,p=1$c2FsdHNhbHRzYWx0c2FsdA$a2V5",
        "$scrypt$r=8,p=1$c2FsdHNhbHRzYWx0c2FsdA$a2V5",
        "$scrypt$ln=4,r=8,p=1$***$***",
    ],
)
def test_a_malformed_hash_is_a_mismatch_and_never_an_error(malformed: str) -> None:
    hasher = _hasher()

    assert hasher.verify(malformed, PASSPHRASE) is False
    assert hasher.needs_rehash(malformed) is False


def test_an_over_long_password_is_refused() -> None:
    hasher = _hasher()
    password_hash = hasher.hash(PASSPHRASE)

    assert hasher.verify(password_hash, "x" * (MAX_PASSWORD_LENGTH + 1)) is False
    with pytest.raises(ValueError, match="too long"):
        hasher.hash("x" * (MAX_PASSWORD_LENGTH + 1))


def test_a_hash_with_other_parameters_needs_rehash() -> None:
    weak, stronger = _hasher(4), _hasher(5)
    weak_hash = weak.hash(PASSPHRASE)

    assert stronger.needs_rehash(weak_hash) is True
    assert weak.needs_rehash(weak_hash) is False
    # A hash keeps verifying with the parameters stored in it, whatever the hasher is set to.
    assert stronger.verify(weak_hash, PASSPHRASE) is True


def test_the_dummy_hash_is_valid_stable_and_matches_nothing_guessable() -> None:
    hasher = _hasher()

    assert hasher.dummy_hash == hasher.dummy_hash
    assert hasher.dummy_hash.startswith("$scrypt$")
    assert hasher.verify(hasher.dummy_hash, PASSPHRASE) is False


def test_the_async_methods_give_the_same_results() -> None:
    hasher = _hasher()

    password_hash = asyncio.run(hasher.hash_async(PASSPHRASE))

    assert asyncio.run(hasher.verify_async(password_hash, PASSPHRASE)) is True
    assert asyncio.run(hasher.verify_async(password_hash, "wrong")) is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"log_n": 3},
        {"log_n": 18},
        {"r": 0},
        {"r": 9},
        {"p": 0},
        {"p": 5},
        {"salt_length": 8},
        {"salt_length": 65},
        {"key_length": 8},
        {"key_length": 65},
    ],
)
def test_out_of_range_parameters_are_rejected(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError, match="must"):
        PasswordHasher(**kwargs)


def test_the_stored_salt_is_random_and_long_enough() -> None:
    salt_text = _hasher().hash(PASSPHRASE).split("$")[3]

    assert len(base64.b64decode(salt_text + "=" * (-len(salt_text) % 4))) >= 16


@pytest.mark.parametrize(
    "malformed",
    [
        "$scrypt$ln=17,r=9,p=1$c2FsdHNhbHRzYWx0c2FsdA$a2V5",
        "$scrypt$ln=17,r=8,p=5$c2FsdHNhbHRzYWx0c2FsdA$a2V5",
        "$scrypt$ln=17,r=8,p=1,r=8$c2FsdHNhbHRzYWx0c2FsdA$a2V5",
        "$scrypt$ln=17,r=8,p=1,unknown=1$c2FsdHNhbHRzYWx0c2FsdA$a2V5",
    ],
)
def test_hashes_with_unsupported_parameters_are_rejected(malformed: str) -> None:
    hasher = PasswordHasher()

    assert hasher.verify(malformed, PASSPHRASE) is False
    assert hasher.needs_rehash(malformed) is False


def test_the_async_dummy_hash_matches_the_sync_dummy_hash() -> None:
    hasher = _hasher()

    async def run() -> None:
        dummy_hash = await hasher.dummy_hash_async()

        assert dummy_hash == hasher.dummy_hash
        assert hasher.verify(dummy_hash, PASSPHRASE) is False

    asyncio.run(run())
