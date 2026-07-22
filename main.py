import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from core.database import init_db, ensure_default_admin
from core.api import auth_router, admin_router, solve_router, history_router

logger = logging.getLogger("planimetry")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await ensure_default_admin()
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
app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(solve_router.router)
app.include_router(history_router.router)


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)