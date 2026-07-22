import re
from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Ім'я користувача має містити щонайменше 3 символи.")
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Ім'я користувача може містити лише латинські літери, цифри та підкреслення.")
        return v

    @field_validator("password")
    @classmethod
    def password_must_be_strong_enough(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль має містити щонайменше 6 символів.")
        if not re.search(r'[A-Za-zА-Яа-яЇїІіЄєҐґ]', v):
            raise ValueError("Пароль має містити щонайменше одну літеру.")
        if not re.search(r'\d', v):
            raise ValueError("Пароль має містити щонайменше одну цифру.")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"