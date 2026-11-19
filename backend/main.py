from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from backend.src.models.tickets import Ticket
from backend.src.routes.tickets import router as tickets_router


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

frontend_url = os.getenv("FRONTEND_URL", "").strip()
allowed_origins = [frontend_url] if frontend_url else ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(tickets_router)

@app.get("/api/health", tags=["Health"])
def home() -> dict[str, str]:
    return {"message": "BonnelaTomate API", "documentation": "/api/docs"}


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"message": "BonnelaTomate API", "documentation": "/api/docs"}