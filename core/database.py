import json
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, DateTime, Text, Integer, select

try:
    KYIV_TZ: timezone | ZoneInfo = ZoneInfo("Europe/Kyiv")
except ZoneInfoNotFoundError:
    KYIV_TZ = timezone(timedelta(hours=3))

DATABASE_URL = "sqlite+aiosqlite:///planimetry.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class SolutionRecord(Base):
    __tablename__ = "solutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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

    def to_dict(self) -> dict:
        # SQLite повертає naive datetime (без timezone).
        # Явно позначаємо як UTC, потім конвертуємо у київський час.
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


async def save_solution(db: AsyncSession, figure: str, task_type: str,
                        params: dict, targets: list, result: dict,
                        steps: list, image: str | None) -> SolutionRecord:
    record = SolutionRecord(
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


async def get_history(db: AsyncSession, limit: int = 50) -> list[SolutionRecord]:
    stmt = select(SolutionRecord).order_by(SolutionRecord.created_at.desc()).limit(limit)
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