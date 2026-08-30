from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.config import settings
from app.api.routes.papers import router as papers_router
from app.api.routes.semantic_search import (
    router as semantic_search_router,
)

app = FastAPI(
    title=settings.app_name,
    description=(
        "An agentic NLP system for searching scientific literature "
        "and building evidence graphs."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix=settings.api_prefix,
)
app.include_router(
    papers_router,
    prefix=settings.api_prefix,
)

app.include_router(
    semantic_search_router,
    prefix=settings.api_prefix,
)
@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to EvidenceGraph API",
        "documentation": "/docs",
        "health": f"{settings.api_prefix}/health",
    }
