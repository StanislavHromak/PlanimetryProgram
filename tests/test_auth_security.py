from datetime import timedelta

from core.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    def test_hash_is_not_plain_password(self):
        hashed = hash_password("MyPassword1")
        assert hashed != "MyPassword1"

    def test_verify_correct_password(self):
        hashed = hash_password("MyPassword1")
        assert verify_password("MyPassword1", hashed) is True

    def test_verify_incorrect_password(self):
        hashed = hash_password("MyPassword1")
        assert verify_password("WrongPassword", hashed) is False

    def test_same_password_produces_different_hashes(self):
        hashed_1 = hash_password("MyPassword1")
        hashed_2 = hash_password("MyPassword1")
        # bcrypt include a random salt, so two hashes of the same password differ
        assert hashed_1 != hashed_2
        assert verify_password("MyPassword1", hashed_1) is True
        assert verify_password("MyPassword1", hashed_2) is True


class TestAccessTokens:
    def test_create_and_decode_roundtrip(self):
        token = create_access_token({"sub": "stanislav"})
        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "stanislav"
        assert "exp" in payload

    def test_decode_invalid_token_returns_none(self):
        assert decode_access_token("not-a-valid-jwt-token") is None

    def test_decode_tampered_token_returns_none(self):
        token = create_access_token({"sub": "stanislav"})
        tampered = token[:-2] + ("aa" if not token.endswith("aa") else "bb")
        assert decode_access_token(tampered) is None

    def test_expired_token_returns_none(self):
        token = create_access_token({"sub": "stanislav"}, expires_delta=timedelta(seconds=-1))
        assert decode_access_token(token) is None