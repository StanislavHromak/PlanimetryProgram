import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user_optional
from core.auth.roles import UserRole
from core.database import get_db, get_history, get_solution_by_id, delete_solution, User
from core.export.pdf_exporter import generate_pdf

router = APIRouter(prefix="/api", tags=["history"])


def _ensure_solution_owner(record, current_user: User | None) -> None:
    if current_user is None:
        raise HTTPException(status_code=401, detail="Необхідна авторизація.")
    if current_user.role == UserRole.ADMIN.value:
        return
    if record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Немає доступу до цього розв'язку.")


@router.get("/history")
async def get_solutions_history(
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    is_admin = current_user is not None and current_user.role == UserRole.ADMIN.value
    user_id = current_user.id if current_user else None
    records = await get_history(db, user_id=user_id, limit=50, include_all=is_admin)
    return {"success": True, "data": [r.to_dict() for r in records]}


@router.get("/history/{solution_id}")
async def get_solution(
    solution_id: int, db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    record = await get_solution_by_id(db, solution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Розв'язок не знайдено")
    _ensure_solution_owner(record, current_user)
    return {"success": True, "data": record.to_dict()}


@router.delete("/history/{solution_id}")
async def remove_solution(
    solution_id: int, db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    record = await get_solution_by_id(db, solution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Розв'язок не знайдено")
    _ensure_solution_owner(record, current_user)
    deleted = await delete_solution(db, solution_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Розв'язок не знайдено")
    return {"success": True}


@router.get("/export/pdf/{solution_id}")
async def export_pdf(
    solution_id: int, db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    record = await get_solution_by_id(db, solution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Розв'язок не знайдено")
    _ensure_solution_owner(record, current_user)
    pdf_bytes = generate_pdf(record.to_dict())
    return StreamingResponse(
        io.BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="solution_{solution_id}.pdf"'},
    )