"""
Tests for the password policy.
"""
import pytest

from app.core.password_policy import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    validate_password,
)


def test_validate_password_accepts_valid_password():
    assert validate_password("Abcdef1_") == "Abcdef1_"


def test_validate_password_accepts_password_at_max_length():
    """
    El máximo se subió de 20 a 50 cuando se agregó el chequeo de los 72 bytes de
    bcrypt: el borde exacto tiene que seguir siendo válido.
    """
    password = "A1_" + "a" * (PASSWORD_MAX_LENGTH - 3)
    assert len(password) == PASSWORD_MAX_LENGTH
    assert validate_password(password) == password


@pytest.mark.parametrize(
    "password",
    [
        "A1_" + "a" * (PASSWORD_MIN_LENGTH - 4),  # < 8 chars
        "abcdefg1_",  # no uppercase
        "Abcdefgh_",  # no digit
        "Abcdefgh1",  # no special (_!?*)
        "A1_" + "a" * (PASSWORD_MAX_LENGTH - 2),  # > 50 chars
    ],
)
def test_validate_password_rejects_invalid_password(password: str):
    with pytest.raises(ValueError):
        validate_password(password)
