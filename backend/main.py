import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from src.models.tickets import Ticket
from src.routes.tickets import router as tickets_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="BonnelaTomate API",
    description="API de gestion des tickets.",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

frontend_url = os.getenv("FRONTEND_URL")
allowed_origins = ["http://localhost:3000"]
if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets_router)

@app.get("/api/health", tags=["Health"])
def home() -> dict[str, str]:
    return {"message": "BonnelaTomate API", "documentation": "/api/docs"}


@app.get("/health", include_in_schema=False)
def health_alias() -> dict[str, str]:
    return {"status": "ok"}