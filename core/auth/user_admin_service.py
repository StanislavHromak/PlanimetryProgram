from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.roles import UserRole
from core.database import User, set_user_active, set_user_role, delete_user


class UserAdminService:
    """
    Інкапсулює адміністративні операції над обліковими записами користувачів.

    Клас навмисно не побудований як ієрархія Command/Strategy: усі операції —
    це прості одноразові дії над одним записом без варіативної поведінки чи
    потреби в поліморфному переборі, тож повноцінна патернова абстракція
    була б невиправданим ускладненням (YAGNI). Інкапсуляція в сервісному
    класі забезпечує єдину відповідальність і уникає розмазування бізнес-логіки
    по ендпоінтах FastAPI.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def block(self, user: User) -> User:
        return await set_user_active(self._db, user, False)

    async def unblock(self, user: User) -> User:
        return await set_user_active(self._db, user, True)

    async def change_role(self, user: User, role: str) -> User:
        if role not in (UserRole.USER.value, UserRole.ADMIN.value):
            raise ValueError("Некоректна роль.")
        return await set_user_role(self._db, user, role)

    async def remove(self, user: User) -> None:
        await delete_user(self._db, user)