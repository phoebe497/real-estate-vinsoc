import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api.agent_routes import router as agent_router
from src.api.routes import router
from src.api.zone_routes import router as zone_router
from src.config import get_settings
from src.db.seed import seed_catalog
from src.db.seed_admin import seed_admin
from src.db.seed_permissions import seed_permissions
from src.db.session import get_engine, get_session_factory, init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)

    settings = get_settings()
    print(f"[START] {settings.app_name} in {settings.app_env} mode")

    if settings.auto_create_tables:
        init_database()

    if settings.auto_seed_catalog:
        with get_session_factory()() as session:
            seed_catalog(session)
            seed_admin(session, settings)
            seed_permissions(session)

    yield

    print("[STOP] Shutting down...")


settings = get_settings()

# Log input/output từng node agent (agent.intent_node, agent.rag_node,
# agent.profile_node, agent.llm_node) theo LOG_LEVEL trong .env.
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="Vinhomes AI Real Estate API",
    description="AI Pre-Sales Advisor cho Vinhomes Ocean Park",
    version=settings.app_version,
    lifespan=lifespan,
)

# PUT/DELETE bắt buộc cho API V2 (PUT /sales/{id}/permissions, DELETE fallback-rules...).
# Thiếu chúng, preflight OPTIONS bị từ chối → browser báo lỗi CORS (bug P1).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Internal / legacy API (kept for backward compatibility)
app.include_router(router, prefix="/api/v1")
app.include_router(zone_router, prefix="/api/v1")

# Primary AI agent API
app.include_router(agent_router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env, "app": settings.app_name}


@app.get("/ready")
async def ready():
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
