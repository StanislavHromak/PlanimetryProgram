import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from schemas import GeometryRequest
from core.factory import GeometryFactory, GUEST_ALLOWED_FIGURES
from core.auth.schemas import UserCreate, UserLogin, Token, UserOut
from core.auth.security import hash_password, verify_password, create_access_token
from core.auth.dependencies import get_current_user, get_current_user_optional
from core.database import (
    init_db, get_db,
    save_solution, get_history,
    get_solution_by_id, delete_solution,
    create_user, get_user_by_username, User,
)

from core.export.pdf_exporter import generate_pdf

logger = logging.getLogger("planimetry")

@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Universal Planimetry Solver API", lifespan=lifespan)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Необроблена помилка на %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": f"Внутрішня помилка сервера: {exc}"},
    )

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


# --- Авторизація ---

@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Користувач з таким іменем вже існує.")

    hashed = hash_password(user_data.password)
    user = await create_user(db, user_data.username, hashed)
    token = create_access_token({"sub": str(user.username)})
    return Token(access_token=token)


@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, credentials.username)
    if not user or not verify_password(credentials.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Невірне ім'я користувача або пароль.")

    token = create_access_token({"sub": str(user.username)})
    return Token(access_token=token)


@app.get("/api/auth/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, username=current_user.username)


# --- Розв'язання задачі (оновлено: опційна авторизація) ---

@app.post("/api/solve")
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
            figure=request.figure,
            task_type=request.task_type,
            params=request.params,
            targets=request.targets,
        )
        result = solver.calculate()

        if result.get("success"):
            await save_solution(
                db=db,
                figure=request.figure,
                task_type=request.task_type,
                params=request.params,
                targets=request.targets,
                result=result.get("data", {}),
                steps=result.get("steps", []),
                image=result.get("image"),
                user_id=current_user.id if current_user else None,
            )

        return result

    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": f"Внутрішня помилка сервера: {str(e)}"}


# Історія
@app.get("/api/history")
async def get_solutions_history(
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    records = await get_history(db, user_id=user_id, limit=50)
    return {"success": True, "data": [r.to_dict() for r in records]}


@app.get("/api/history/{solution_id}")
async def get_solution(solution_id: int, db: AsyncSession = Depends(get_db)):
    record = await get_solution_by_id(db, solution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Розв'язок не знайдено")
    return {"success": True, "data": record.to_dict()}


@app.delete("/api/history/{solution_id}")
async def remove_solution(solution_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_solution(db, solution_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Розв'язок не знайдено")
    return {"success": True}


# Експорт PDF
@app.get("/api/export/pdf/{solution_id}")
async def export_pdf(solution_id: int, db: AsyncSession = Depends(get_db)):
    record = await get_solution_by_id(db, solution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Розв'язок не знайдено")

    pdf_bytes = generate_pdf(record.to_dict())

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="solution_{solution_id}.pdf"'
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)