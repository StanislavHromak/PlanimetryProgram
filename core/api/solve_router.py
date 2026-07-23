from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import GeometryRequest
from core.factory import GeometryFactory, GUEST_ALLOWED_FIGURES
from core.auth.dependencies import get_current_user_optional
from core.database import get_db, save_solution, User

router = APIRouter(prefix="/api", tags=["solve"])


@router.post("/solve")
async def solve_geometry(
    request: GeometryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if current_user is None and request.figure not in GUEST_ALLOWED_FIGURES:
        return {
            "success": False,
            "error": (
                "Ця фігура доступна лише зареєстрованим користувачам. "
                "Будь ласка, увійдіть або зареєструйтесь, щоб продовжити."
            ),
        }
    try:
        solver = GeometryFactory.create_solver(
            figure=request.figure, task_type=request.task_type,
            params=request.params, targets=request.targets,
        )
        result = solver.calculate()
        if result.get("success"):
            await save_solution(
                db=db, figure=request.figure, task_type=request.task_type,
                params=request.params, targets=request.targets,
                result=result.get("data", {}), steps=result.get("steps", []),
                image=result.get("image"),
                user_id=current_user.id if current_user else None,
            )
        return result
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": f"Внутрішня помилка сервера: {str(e)}"}