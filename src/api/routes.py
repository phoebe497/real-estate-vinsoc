"""Router tổng cho /api/v1 — gom các router V2 (BAN_THIET_KE_V2 Mục 8)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.api.auth import router as auth_router
from src.api.catalog import router as catalog_router
from src.api.customers import router as customers_router
from src.api.dashboard import router as dashboard_router
from src.api.fallback import router as fallback_router
from src.api.sales import router as sales_router

router = APIRouter()

router.include_router(catalog_router)
router.include_router(customers_router)
router.include_router(auth_router)
router.include_router(sales_router)
router.include_router(dashboard_router)
router.include_router(fallback_router)


# ── Legacy endpoints giữ tương thích client cũ ───────────────────────────────


class LegacyChatRequest(BaseModel):
    message: str = Field(min_length=1)


@router.post("/chat")
async def legacy_chat(data: LegacyChatRequest):
    """Backward-compatible chat endpoint kept for older clients/tests."""
    return {"response": data.message, "analysis": ""}


@router.get("/status")
async def api_status():
    """Kiểm tra trạng thái API và version."""
    return {
        "status": "ready",
        "agent": "Vinhomes AI Advisor v2.0",
        "features": ["intent-detection", "rag-zone-matching", "lead-capture-gating"],
    }
