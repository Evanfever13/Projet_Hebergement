from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from backend.database import Base, engine
from backend.src.routes.tickets import router as tickets_router
from backend.src.routes.users import router2 as auth_router, users_router

if (os.getenv("VERCEL") == "1" or os.getenv("RENDER") == "true") and not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY must be configured in production.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="BonnelaTomate API",
    description="API d'authentification et de gestion des tickets.",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tickets_router)

@app.get("/api/health", tags=["Health"])
def home() -> dict[str, str]:
    return {"message": "BonnelaTomate API", "documentation": "/api/docs"}


@app.get("/health", include_in_schema=False)
def health_alias() -> dict[str, str]:
    return {"status": "ok"}