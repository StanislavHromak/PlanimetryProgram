import json
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Text, Integer, ForeignKey, Boolean, select
from sqlalchemy import delete as sa_delete

try:
    KYIV_TZ: timezone | ZoneInfo = ZoneInfo("Europe/Kyiv")
except ZoneInfoNotFoundError:
    KYIV_TZ = timezone(timedelta(hours=3))

DATABASE_URL = "sqlite+aiosqlite:///planimetry.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовий клас для всіх декларативних моделей SQLAlchemy."""
    pass


class User(Base):
    """Модель зареєстрованого користувача системи."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    solutions: Mapped[list["SolutionRecord"]] = relationship(back_populates="user")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M") if self.created_at else None,
        }


class SolutionRecord(Base):
    """
        Модель бази даних для збереження історії розв'язаних задач з планіметрії.

        Зберігає інформацію про фігуру, тип задачі, вхідні параметри, цілі,
        покроковий розв'язок, фінальний результат та згенероване креслення (base64).
        Прив'язана до користувача опційно — гості також можуть розв'язувати задачі,
        але без збереження персональної історії.
    """
    __tablename__ = "solutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    figure: Mapped[str] = mapped_column(String(50))
    task_type: Mapped[str] = mapped_column(String(50))
    params_json: Mapped[str] = mapped_column(Text)
    targets_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    steps_json: Mapped[str] = mapped_column(Text)
    image_base64: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User | None"] = relationship(back_populates="solutions")

    def to_dict(self) -> dict:
        dt = self.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        kyiv_dt = dt.astimezone(KYIV_TZ)
        return {
            "id": self.id,
            "created_at": kyiv_dt.strftime("%d.%m.%Y %H:%M"),
            "figure": self.figure,
            "task_type": self.task_type,
            "params": json.loads(self.params_json),
            "targets": json.loads(self.targets_json),
            "result": json.loads(self.result_json),
            "steps": json.loads(self.steps_json),
            "image": self.image_base64,
        }


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Користувачі

async def create_user(db: AsyncSession, username: str, hashed_password: str) -> User:
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession, limit: int = 100, offset: int = 0) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def username_taken_by_other(db: AsyncSession, username: str, exclude_user_id: int) -> bool:
    stmt = select(User).where(User.username == username, User.id != exclude_user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def update_profile(db: AsyncSession, user: User, **fields) -> User:
    for key, value in fields.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(db: AsyncSession, user: User, new_hashed_password: str) -> None:
    user.hashed_password = new_hashed_password
    await db.commit()


async def set_user_active(db: AsyncSession, user: User, is_active: bool) -> User:
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    return user


async def set_user_role(db: AsyncSession, user: User, role: str) -> User:
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    """Видаляє акаунт користувача разом з усією його історією розв'язків (каскадно)."""
    await db.execute(sa_delete(SolutionRecord).where(SolutionRecord.user_id == user.id))
    await db.delete(user)
    await db.commit()


async def ensure_default_admin() -> None:
    """Створює або підвищує адміністратора за замовчуванням із середовища при старті."""
    admin_username = os.getenv("DEFAULT_ADMIN_USERNAME")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    if not admin_username or not admin_password:
        return

    from core.auth.security import hash_password

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.role == "admin")
        result = await session.execute(stmt)
        if result.scalar_one_or_none() is not None:
            return

        existing = await get_user_by_username(session, admin_username)
        if existing is not None:
            existing.role = "admin"
            await session.commit()
            return

        admin = User(
            username=admin_username,
            hashed_password=hash_password(admin_password),
            role="admin",
        )
        session.add(admin)
        await session.commit()


# Розв'язки

async def save_solution(db: AsyncSession, figure: str, task_type: str,
                        params: dict, targets: list, result: dict,
                        steps: list, image: str | None,
                        user_id: int | None = None) -> SolutionRecord:
    record = SolutionRecord(
        user_id=user_id,
        figure=figure,
        task_type=task_type,
        params_json=json.dumps(params, ensure_ascii=False),
        targets_json=json.dumps(targets, ensure_ascii=False),
        result_json=json.dumps(result, ensure_ascii=False),
        steps_json=json.dumps(steps, ensure_ascii=False),
        image_base64=image,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_history(
    db: AsyncSession,
    user_id: int | None = None,
    limit: int = 50,
    include_all: bool = False,
) -> list[SolutionRecord]:
    """
    Повертає історію. Звичайний користувач бачить лише свої записи.
    Адміністратор (include_all=True) бачить історію всіх користувачів.
    Гість (user_id is None і include_all=False) отримує порожній список.
    """
    stmt = select(SolutionRecord).order_by(SolutionRecord.created_at.desc()).limit(limit)

    if include_all:
        result = await db.execute(stmt)
        return list(result.scalars().all())

    if user_id is None:
        return []

    stmt = stmt.where(SolutionRecord.user_id == user_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_solution_by_id(db: AsyncSession, solution_id: int) -> SolutionRecord | None:
    stmt = select(SolutionRecord).where(SolutionRecord.id == solution_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_solution(db: AsyncSession, solution_id: int) -> bool:
    record = await get_solution_by_id(db, solution_id)
    if not record:
        return False
    await db.delete(record)
    await db.commit()
    return True