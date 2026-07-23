from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_admin_user
from core.auth.schemas import AdminRoleUpdate
from core.auth.user_admin_service import UserAdminService
from core.database import get_db, get_all_users, get_user_by_id, User

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def _get_target_user(db: AsyncSession, admin: User, user_id: int) -> User:
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Не можна виконувати дії над власним акаунтом.")
    target = await get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Користувача не знайдено.")
    return target


@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db), _admin: User = Depends(get_current_admin_user)):
    users = await get_all_users(db)
    return {"success": True, "data": [u.to_dict() for u in users]}


@router.post("/users/{user_id}/block")
async def block_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    target = await _get_target_user(db, admin, user_id)
    updated = await UserAdminService(db).block(target)
    return {"success": True, "data": updated.to_dict()}


@router.post("/users/{user_id}/unblock")
async def unblock_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    target = await _get_target_user(db, admin, user_id)
    updated = await UserAdminService(db).unblock(target)
    return {"success": True, "data": updated.to_dict()}


@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: int, payload: AdminRoleUpdate,
    db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin_user),
):
    target = await _get_target_user(db, admin, user_id)
    try:
        updated = await UserAdminService(db).change_role(target, payload.role)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return {"success": True, "data": updated.to_dict()}


@router.delete("/users/{user_id}")
async def remove_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    target = await _get_target_user(db, admin, user_id)
    username = target.username
    await UserAdminService(db).remove(target)
    return {"success": True, "detail": f"Акаунт користувача {username} видалено."}

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    target = await get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Користувача не знайдено.")
    return {"success": True, "data": target.to_dict()}