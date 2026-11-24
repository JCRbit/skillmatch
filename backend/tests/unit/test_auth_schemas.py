import pytest
from pydantic import ValidationError

from skillmatch.modules.identity.models import UserRole
from skillmatch.modules.identity.schemas import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    LoginRequest,
    PublicRole,
    RegisterRequest,
)

VALID_PASSWORD = "x" * PASSWORD_MIN_LENGTH
SHORT_LOGIN_PASSWORD = "p"  # noqa: S105 - synthetic fixture value


def _register(**overrides: object) -> RegisterRequest:
    data = {"email": "ana@skillmatch.test", "password": VALID_PASSWORD, "role": "talento"}
    return RegisterRequest.model_validate({**data, **overrides})


def test_the_email_is_trimmed_and_lower_cased() -> None:
    assert _register(email="  Ana.Lopez@SkillMatch.TEST ").email == "ana.lopez@skillmatch.test"


@pytest.mark.parametrize("role", ["talento", "empresa"])
def test_public_roles_are_accepted(role: str) -> None:
    assert _register(role=role).role.to_user_role() is UserRole(role)


@pytest.mark.parametrize("role", ["admin", "ADMIN", "Talento", "candidate", "", None])
def test_every_other_role_is_rejected_and_admin_is_never_self_service(role: object) -> None:
    with pytest.raises(ValidationError):
        _register(role=role)


def test_the_public_roles_are_exactly_the_two_self_service_ones() -> None:
    assert {role.value for role in PublicRole} == {"talento", "empresa"}
    assert UserRole.ADMIN.value not in {role.value for role in PublicRole}


@pytest.mark.parametrize(
    "email",
    ["", "plain", "a@b", "@skillmatch.test", "a b@skillmatch.test", "a@@skillmatch.test", 42],
)
def test_malformed_emails_are_rejected(email: object) -> None:
    with pytest.raises(ValidationError):
        _register(email=email)


def test_an_email_longer_than_254_characters_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _register(email="a" * 250 + "@skillmatch.test")


@pytest.mark.parametrize(
    "password",
    ["short", " " * PASSWORD_MIN_LENGTH, "x" * (PASSWORD_MAX_LENGTH + 1), None, 12345678901234],
    ids=["too-short", "only-whitespace", "too-long", "null", "not-a-string"],
)
def test_passwords_outside_the_policy_are_rejected(password: object) -> None:
    with pytest.raises(ValidationError):
        _register(password=password)


def test_the_password_does_not_appear_in_the_representation() -> None:
    assert VALID_PASSWORD not in repr(_register())


@pytest.mark.parametrize("extra", ["status", "is_admin", "id", "password_hash"])
def test_unknown_fields_are_rejected_on_registration(extra: str) -> None:
    with pytest.raises(ValidationError):
        _register(**{extra: "anything"})


def test_login_has_no_role_field_so_the_client_cannot_choose_one() -> None:
    assert "role" not in LoginRequest.model_fields
    with pytest.raises(ValidationError):
        LoginRequest.model_validate(
            {"email": "ana@skillmatch.test", "password": "anything", "role": "admin"}
        )


def test_login_accepts_any_non_empty_password_up_to_the_limit() -> None:
    assert (
        LoginRequest(email="ana@skillmatch.test", password=SHORT_LOGIN_PASSWORD).password
        == SHORT_LOGIN_PASSWORD
    )
    with pytest.raises(ValidationError):
        LoginRequest(email="ana@skillmatch.test", password="")
