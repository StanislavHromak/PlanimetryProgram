from pydantic import BaseModel, field_validator
from core.auth.validators import validate_username_format, validate_password_strength
from core.auth.roles import UserRole


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        return validate_username_format(v)

    @field_validator("password")
    @classmethod
    def password_must_be_strong_enough(cls, v: str) -> str:
        return validate_password_strength(v)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    role: str
    is_active: bool
    display_name: str | None = None
    email: str | None = None


class ProfileUpdate(BaseModel):
    username: str | None = None
    display_name: str | None = None
    email: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        return validate_username_format(v) if v is not None else v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v:
            return None
        import re
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Некоректний формат електронної пошти.")
        return v


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_must_be_strong(cls, v: str) -> str:
        return validate_password_strength(v)


class AdminRoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v: str) -> str:
        if v not in (UserRole.USER.value, UserRole.ADMIN.value):
            raise ValueError("Роль має бути 'user' або 'admin'.")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"