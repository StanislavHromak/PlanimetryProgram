from enum import Enum


class UserRole(str, Enum):
    """Ролі користувачів системи."""
    USER = "user"
    ADMIN = "admin"