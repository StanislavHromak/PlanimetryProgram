from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from schemas import GeometryRequest
from core.factory import GeometryFactory

app = FastAPI(title="Universal Planimetry Solver API")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    """Віддає головну сторінку при вході на сайт."""
    return FileResponse('static/index.html')


@app.post("/api/solve")
async def solve_geometry(request: GeometryRequest):
    """
    Універсальний ендпоінт для всіх геометричних задач.
    """
    try:
        solver = GeometryFactory.create_solver(
            figure=request.figure,
            task_type=request.task_type,
            params=request.params,
            targets=request.targets
        )

        result = solver.calculate()
        return result

    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        return {"success": False, "error": f"Внутрішня помилка сервера: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)