import pytest
from pydantic import ValidationError

from app.modules.identity.schemas import LoginRequest


def test_login_accepts_generated_technical_demo_identifier() -> None:
    request = LoginRequest(email="0001-member-name@demo.local", password="password")

    assert request.email == "0001-member-name@demo.local"


def test_login_keeps_standard_email_validation() -> None:
    request = LoginRequest(email="member@example.org", password="password")

    assert request.email == "member@example.org"


def test_login_accepts_phone_or_simple_identifier() -> None:
    assert LoginRequest(email="+49123456789", password="password").email == "+49123456789"
    assert LoginRequest(email="Marie.Club", password="password").email == "marie.club"


def test_login_rejects_other_reserved_email_domains() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(email="member@demo.local", password="password")
