from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from schemas import GeometryRequest
from core.factory import GeometryFactory
from core.database import (
    init_db, get_db,
    save_solution, get_history,
    get_solution_by_id, delete_solution
)
from core.export.pdf_exporter import generate_pdf


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Universal Planimetry Solver API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


# ── Розв'язання задачі ────────────────────────────────────────────────────────
@app.post("/api/solve")
async def solve_geometry(
    request: GeometryRequest,
    db: AsyncSession = Depends(get_db)
):
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
            )

        return result

    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": f"Внутрішня помилка сервера: {str(e)}"}


# ── Історія ───────────────────────────────────────────────────────────────────
@app.get("/api/history")
async def get_solutions_history(db: AsyncSession = Depends(get_db)):
    records = await get_history(db, limit=50)
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


# ── Експорт PDF ───────────────────────────────────────────────────────────────
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