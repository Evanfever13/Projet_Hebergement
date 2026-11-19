from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URL", "").split(",")
    if origin.strip()
]
allowed_origins.extend([
    "http://localhost:3000",
    "http://127.0.0.1:3000",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(allowed_origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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