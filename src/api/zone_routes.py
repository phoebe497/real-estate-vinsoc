"""FastAPI routes cho Vinhomes Zone data.

GET /zones          → danh sách phân khu (có filter)
GET /zones/{slug}   → chi tiết 1 phân khu + buildings
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.services.vinhomes_data import (
    get_all_zones,
    get_amenities,
    get_buildings_for_zone,
    get_project_info,
    get_transport_routes,
    get_zone_by_slug,
)

router = APIRouter(prefix="/zones", tags=["zones"])


class ZoneListItem(BaseModel):
    name: str
    slug: str
    description: str
    design_style: str
    handover_status: str
    total_buildings: int
    unit_types: list[str]
    price_min_billion: float
    price_max_billion: float
    featured_amenities: list[str]
    target_audience: list[str]
    data_period: str
    confidence_level: str


class BuildingItem(BaseModel):
    name: str
    slug: str
    floors: int
    handover_status: str
    location_note: str
    popular_unit_types: list[str]
    area_min_sqm: float
    area_max_sqm: float


class ZoneDetail(ZoneListItem):
    location_in_project: str
    buildings: list[BuildingItem]
    amenities: list[dict]
    transport_routes: list[dict]


class ZoneListResponse(BaseModel):
    total: int
    items: list[ZoneListItem]


class ProjectOverview(BaseModel):
    name: str
    developer: str
    location: str
    total_area_ha: int
    description: str
    highlights: list[str]


def _zone_to_item(z: dict) -> ZoneListItem:
    price = z.get("total_price_range_billion", {})
    return ZoneListItem(
        name=z["name"],
        slug=z["slug"],
        description=z.get("description", ""),
        design_style=z.get("design_style", ""),
        handover_status=z.get("handover_status", ""),
        total_buildings=z.get("total_buildings", 0),
        unit_types=z.get("unit_types", []),
        price_min_billion=price.get("min", 0),
        price_max_billion=price.get("max", 0),
        featured_amenities=z.get("featured_amenities", []),
        target_audience=z.get("target_audience", []),
        data_period=z.get("data_period", ""),
        confidence_level=z.get("confidence_level", "medium"),
    )


# ── GET /zones ───────────────────────────────────────────────────────────────

@router.get("", response_model=ZoneListResponse)
async def list_zones(
    handover_status: str | None = Query(None, description="handed_over | under_construction"),
    max_price_billion: float | None = Query(None, description="Lọc theo giá tối đa (tỷ)"),
    unit_type: str | None = Query(None, description="Lọc theo loại căn: 2PN, 3PN..."),
) -> ZoneListResponse:
    """Danh sách tất cả phân khu Vinhomes Ocean Park."""
    zones = get_all_zones()

    if handover_status:
        zones = [z for z in zones if z.get("handover_status") == handover_status]

    if max_price_billion is not None:
        zones = [
            z for z in zones
            if z.get("total_price_range_billion", {}).get("min", 9999) <= max_price_billion
        ]

    if unit_type:
        zones = [
            z for z in zones
            if any(unit_type.lower() in t.lower() for t in z.get("unit_types", []))
        ]

    return ZoneListResponse(
        total=len(zones),
        items=[_zone_to_item(z) for z in zones],
    )


# ── GET /zones/{slug} ────────────────────────────────────────────────────────

@router.get("/{slug}", response_model=ZoneDetail)
async def get_zone(slug: str) -> ZoneDetail:
    """Chi tiết phân khu: thông tin, danh sách tòa, tiện ích, đường đi."""
    zone = get_zone_by_slug(slug)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Phân khu '{slug}' không tìm thấy")

    buildings_raw = get_buildings_for_zone(slug)
    buildings = [
        BuildingItem(
            name=b["name"],
            slug=b["slug"],
            floors=b.get("floors", 0),
            handover_status=b.get("handover_status", ""),
            location_note=b.get("location_note", ""),
            popular_unit_types=b.get("popular_unit_types", []),
            area_min_sqm=b.get("area_range_sqm", {}).get("min", 0),
            area_max_sqm=b.get("area_range_sqm", {}).get("max", 0),
        )
        for b in buildings_raw
    ]

    amenities = get_amenities(zone_slug=slug)
    transport = get_transport_routes()
    price = zone.get("total_price_range_billion", {})

    return ZoneDetail(
        name=zone["name"],
        slug=zone["slug"],
        description=zone.get("description", ""),
        design_style=zone.get("design_style", ""),
        handover_status=zone.get("handover_status", ""),
        total_buildings=zone.get("total_buildings", 0),
        unit_types=zone.get("unit_types", []),
        price_min_billion=price.get("min", 0),
        price_max_billion=price.get("max", 0),
        featured_amenities=zone.get("featured_amenities", []),
        target_audience=zone.get("target_audience", []),
        data_period=zone.get("data_period", ""),
        confidence_level=zone.get("confidence_level", "medium"),
        location_in_project=zone.get("location_in_project", ""),
        buildings=buildings,
        amenities=amenities,
        transport_routes=transport,
    )


# ── GET /project ─────────────────────────────────────────────────────────────

@router.get("/project/overview", response_model=ProjectOverview, tags=["project"])
async def get_project() -> ProjectOverview:
    """Thông tin tổng quan dự án Vinhomes Ocean Park."""
    p = get_project_info()
    return ProjectOverview(**p)
