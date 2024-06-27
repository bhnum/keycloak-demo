from fastapi import FastAPI, Request, status
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DatabaseError

from app.database import engine
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(root_path="/api", docs_url="/", lifespan=lifespan)

app.include_router(router)


@app.exception_handler(DatabaseError)
async def db_error_exception_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Database Error", "db_errors": exc.args},
    )
