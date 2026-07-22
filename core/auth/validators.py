import re


def validate_username_format(value: str) -> str:
    if len(value) < 3:
        raise ValueError("Ім'я користувача має містити щонайменше 3 символи.")
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValueError("Ім'я користувача може містити лише латинські літери, цифри та підкреслення.")
    return value


def validate_password_strength(value: str) -> str:
    if len(value) < 6:
        raise ValueError("Пароль має містити щонайменше 6 символів.")
    if not re.search(r'[A-Za-zА-Яа-яЇїІіЄєҐґ]', value):
        raise ValueError("Пароль має містити щонайменше одну літеру.")
    if not re.search(r'\d', value):
        raise ValueError("Пароль має містити щонайменше одну цифру.")
    return value