from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.security import decode_access_token
from core.auth.roles import UserRole
from core.database import get_db, get_user_by_username, User


async def _extract_user(authorization: str | None, db: AsyncSession) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    user = await get_user_by_username(db, payload["sub"])
    if user is not None and not user.is_active:
        # Заблокований/видалений користувач: токен перестає діяти без окремого чорного списку.
        return None
    return user


async def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Повертає користувача, якщо токен валідний, інакше None (для гостьового доступу)."""
    return await _extract_user(authorization, db)


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Вимагає валідний токен. Використовується для ендпоінтів, доступних лише авторизованим."""
    user = await _extract_user(authorization, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Необхідна авторизація.")
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Вимагає роль адміністратора."""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Доступ дозволено лише адміністраторам.")
    return current_user