from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.schemas import UserCreate, UserLogin, Token, UserOut, PasswordUpdate
from core.auth.security import hash_password, verify_password, create_access_token
from core.auth.dependencies import get_current_user
from core.database import (
    get_db, create_user, get_user_by_username,
    update_password, username_taken_by_other, delete_user, User,
)
from core.auth.schemas import ProfileUpdate
from core.database import update_profile

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Користувач з таким іменем вже існує.")
    hashed = hash_password(user_data.password)
    user = await create_user(db, user_data.username, hashed)
    token = create_access_token({"sub": str(user.username)})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, credentials.username)
    if not user or not verify_password(credentials.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Невірне ім'я користувача або пароль.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Ваш акаунт заблоковано.")

    token = create_access_token({"sub": str(user.username)})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)

@router.patch("/me", response_model=UserOut)
async def update_my_profile(
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updates = payload.model_dump(exclude_unset=True)
    if "username" in updates:
        if await username_taken_by_other(db, updates["username"], current_user.id):
            raise HTTPException(status_code=400, detail="Це ім'я вже зайняте.")
    updated = await update_profile(db, current_user, **updates)
    return UserOut.model_validate(updated)


@router.patch("/me/password")
async def change_my_password(
    payload: PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, str(current_user.hashed_password)):
        raise HTTPException(status_code=401, detail="Поточний пароль невірний.")
    await update_password(db, current_user, hash_password(payload.new_password))
    return {"success": True, "detail": "Пароль оновлено."}


@router.delete("/me")
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await delete_user(db, current_user)
    return {"success": True, "detail": "Акаунт видалено."}