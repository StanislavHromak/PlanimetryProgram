import pytest

from core.auth.validators import validate_username_format, validate_password_strength


class TestValidateUsernameFormat:
    def test_valid_username_passes(self):
        assert validate_username_format("stas_2005") == "stas_2005"

    def test_too_short_username_raises(self):
        with pytest.raises(ValueError, match="щонайменше 3 символи"):
            validate_username_format("ab")

    @pytest.mark.parametrize("username", [
        "stas!",
        "стас",
        "user name",
        "user@site",
    ])
    def test_invalid_characters_raise(self, username):
        with pytest.raises(ValueError, match="латинські літери"):
            validate_username_format(username)


class TestValidatePasswordStrength:
    def test_valid_password_passes(self):
        assert validate_password_strength("Passw0rd") == "Passw0rd"

    def test_too_short_password_raises(self):
        with pytest.raises(ValueError, match="щонайменше 6 символів"):
            validate_password_strength("a1b2")

    def test_password_without_letter_raises(self):
        with pytest.raises(ValueError, match="одну літеру"):
            validate_password_strength("123456")

    def test_password_without_digit_raises(self):
        with pytest.raises(ValueError, match="одну цифру"):
            validate_password_strength("password")

    def test_password_with_cyrillic_letter_passes(self):
        assert validate_password_strength("Пароль1") == "Пароль1"