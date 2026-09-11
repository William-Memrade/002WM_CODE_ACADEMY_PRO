"""
Tests for the password policy.
"""
import pytest

from app.core.password_policy import validate_password


def test_validate_password_accepts_valid_password():
    """
    Test that validate_password accepts a valid password.
    """
    result = validate_password("Abcdef1_")
    if result != "Abcdef1_":
        pytest.fail(f"Expected 'Abcdef1_', got '{result}'")


@pytest.mark.parametrize(
    "password",
    [
        "A1_aaaa",  # < 8 chars
        "abcdefg1_",  # no uppercase
        "Abcdefgh_",  # no digit
        "Abcdefgh1",  # no special (_!?*)
        "A1_" + ("a" * 18),  # > 20 chars
    ],
)
def test_validate_password_rejects_invalid_password(password: str):
    """
    Test that validate_password rejects invalid passwords.

    Args:
        password (str): _description_
    """
    with pytest.raises(ValueError):
        validate_password(password)
