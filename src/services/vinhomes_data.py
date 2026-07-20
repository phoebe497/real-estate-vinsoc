"""Read, normalize and cache Vinhomes cleaned data for API and AI Agent routes."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from src.config import get_settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROJECT_OVERVIEW = {
    "name": "Vinhomes Ocean Park Gia Lâm",
    "location": "Gia Lâm, Hà Nội",
    "description": (
        "Đại đô thị Vinhomes Ocean Park Gia Lâm với hệ sinh thái căn hộ, "
        "biển hồ, trường học, bệnh viện, thương mại và không gian sống xanh."
    ),
    "highlights": [
        "Biển hồ nước mặn Crystal Lagoons rộng 6.1ha",
        "Hồ Ngọc Trai rộng 24.5ha",
        "Vincom Mega Mall Ocean Park",
        "VinUniversity",
        "Vinschool",
        "Vinmec",
    ],
}

UNKNOWN_VALUE_MARKERS = (
    "chưa cập nhật",
    "chua cap nhat",
    "đang cập nhật",
    "dang cap nhat",
    "liên hệ",
    "lien he",
    "đã bán hết",
    "da ban het",
)


@lru_cache(maxsize=1)
def load_cleaned_zones_data() -> dict:
    """Load cleaned_apartment_zones.json if available."""
    paths_to_try = [
        PROJECT_ROOT / "cleaned_data" / "cleaned_apartment_zones.json",
        PROJECT_ROOT / "data" / "cleaned_apartment_zones.json",
    ]
    for path in paths_to_try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                payload = json.load(f)
            return payload if isinstance(payload, dict) else {}
    return {}


@lru_cache(maxsize=1)
def load_knowledge_chunks() -> list[dict]:
    """Load AI-ready knowledge chunks if available."""
    paths_to_try = [
        PROJECT_ROOT / "cleaned_data" / "ai_knowledge_chunks.json",
        PROJECT_ROOT / "data" / "ai_knowledge_chunks.json",
    ]
    for path in paths_to_try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                payload = json.load(f)
            return payload if isinstance(payload, list) else []
    return []


def _normalize_search_text(value: str) -> str:
    """Normalize text for lightweight lexical search over local knowledge chunks."""
    return re.sub(r"\s+", " ", value.lower()).strip()


def search_knowledge_chunks(query: str, top_k: int = 5) -> list[dict]:
    """Return the most relevant local knowledge chunks for a query.

    This is a backward-compatible helper used by older RAG tests and by any
    lightweight retrieval path that does not require pgvector. It intentionally
    stays dependency-free: score chunks by keyword overlap against subdivision,
    topic and content, then return a normalized copy with `chunk_id`.
    """
    normalized_query = _normalize_search_text(query)
    if not normalized_query:
        return []

    query_terms = {
        term
        for term in re.findall(r"\w+", normalized_query, flags=re.IGNORECASE)
        if len(term) >= 2
    }
    chunks = load_knowledge_chunks()
    scored_chunks: list[tuple[int, int, dict]] = []

    for index, chunk in enumerate(chunks):
        haystack = _normalize_search_text(
            " ".join(
                str(chunk.get(field, ""))
                for field in ("subdivision_slug", "subdivision_name", "topic", "content")
            )
        )
        if not haystack:
            continue

        score = sum(1 for term in query_terms if term in haystack)
        if normalized_query in haystack:
            score += 5
        if score <= 0:
            continue

        normalized_chunk = dict(chunk)
        normalized_chunk.setdefault(
            "chunk_id",
            f"{normalized_chunk.get('subdivision_slug', 'project')}:{normalized_chunk.get('topic', 'general')}:{index}",
        )
        normalized_chunk.setdefault("source_type", "knowledge_chunk")
        normalized_chunk.setdefault("source_url", f"/phan-khu/{normalized_chunk.get('subdivision_slug', '')}")
        normalized_chunk["relevance_score"] = score
        scored_chunks.append((score, -index, normalized_chunk))

    scored_chunks.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [chunk for _, _, chunk in scored_chunks[: max(1, top_k)]]


def _parse_billion_range(price_text: str | None) -> dict:
    """Parse Vietnamese price text like '3,0 - 3,5 tỷ' to a billion-VND range."""
    if not price_text:
        return {}

    normalized = price_text.strip().lower()
    if any(marker in normalized for marker in UNKNOWN_VALUE_MARKERS):
        return {}

    numbers = [
        float(match.replace(",", "."))
        for match in re.findall(r"\d+(?:[,.]\d+)?", normalized)
    ]
    if not numbers:
        return {}

    multiplier = 1.0
    if "triệu" in normalized or "trieu" in normalized:
        multiplier = 0.001

    values = [number * multiplier for number in numbers]
    return {"min": min(values), "max": max(values)}


def _format_billion(value: float | int | None) -> str:
    if value is None:
        return "?"
    text = f"{float(value):.1f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def format_price_range(price_range: dict, fallback: str = "Chưa cập nhật") -> str:
    """Format a parsed billion-VND range for context/response metadata."""
    if not price_range:
        return fallback
    return f"{_format_billion(price_range.get('min'))} - {_format_billion(price_range.get('max'))} tỷ"


def _normalize_apartment_specs(specs: dict) -> tuple[dict, list[str], dict]:
    normalized_specs: dict = {}
    unit_types: list[str] = []
    ranges: list[dict] = []

    for unit_type, spec in specs.items():
        if not isinstance(spec, dict):
            continue

        area_note = spec.get("area") or "Chưa cập nhật"
        price_note = spec.get("price") or "Chưa cập nhật"
        price_range = _parse_billion_range(price_note)
        normalized_specs[unit_type] = {
            "area": area_note,
            "price": price_note,
            "price_range_billion": price_range,
        }
        unit_types.append(unit_type)
        if price_range:
            ranges.append(price_range)

    total_price_range = {}
    if ranges:
        total_price_range = {
            "min": min(item["min"] for item in ranges),
            "max": max(item["max"] for item in ranges),
        }

    return normalized_specs, unit_types, total_price_range


def _zone_from_cleaned(slug: str, data: dict) -> dict:
    specs, unit_types, total_price_range = _normalize_apartment_specs(data.get("apartment_specs", {}))
    return {
        "slug": slug,
        "name": data.get("name", slug),
        "developer": data.get("developer", ""),
        "scale": data.get("scale", ""),
        "description": data.get("introduction", ""),
        "introduction": data.get("introduction", ""),
        "handover_status": data.get("handover_status", ""),
        "handover_standard": data.get("handover_standard", ""),
        "legal_status": data.get("legal_status", ""),
        "location_in_project": data.get("location", ""),
        "design_style": data.get("design_style", ""),
        "apartment_specs": specs,
        "unit_types": unit_types,
        "total_price_range_billion": total_price_range,
        "internal_amenities": data.get("internal_amenities", []) or [],
        "external_amenities": data.get("external_amenities", []) or [],
        "sales_policies": data.get("sales_policies", []) or [],
    }


def _seed_from_cleaned_zones() -> dict:
    cleaned_zones = load_cleaned_zones_data()
    zones = [_zone_from_cleaned(slug, data) for slug, data in cleaned_zones.items()]
    return {
        "project": PROJECT_OVERVIEW,
        "zones": zones,
        "buildings": [],
        "amenities": [
            {
                "zone_slug": zone["slug"],
                "name": amenity,
                "type": scope,
                "scope": scope,
                "description": amenity,
                "distance_text": "",
            }
            for zone in zones
            for scope, source in (
                ("internal", zone.get("internal_amenities", [])),
                ("external", zone.get("external_amenities", [])),
            )
            for amenity in source
        ],
        "transport_routes": [],
        "matching_rules": {},
    }


@lru_cache(maxsize=1)
def load_seed_data() -> dict:
    """Load canonical cleaned zones first; fallback to legacy seed data."""
    cleaned_seed = _seed_from_cleaned_zones()
    if cleaned_seed.get("zones"):
        return cleaned_seed

    settings = get_settings()
    paths_to_try = [
        Path(settings.vinhomes_seed_path),
        PROJECT_ROOT / "data" / "vinhomes_real.json",
    ]
    for seed_path in paths_to_try:
        if seed_path.exists():
            with open(seed_path, encoding="utf-8") as f:
                return json.load(f)
    return _seed_from_cleaned_zones()


def map_slug_to_cleaned_key(slug: str) -> str:
    """Map legacy seed slugs to cleaned_apartment_zones.json keys."""
    base = slug[:-9] if slug.endswith("-vinhomes") else slug
    if base == "sapphire":
        return "the-sapphire"
    return base


def map_cleaned_key_to_seed_slug(cleaned_key: str) -> str:
    """Map a cleaned-data subdivision key to the public seed slug when possible."""
    if cleaned_key in load_cleaned_zones_data() and not cleaned_key.endswith("-vinhomes"):
        return f"{cleaned_key}-vinhomes"
    for zone in get_all_zones():
        slug = zone.get("slug", "")
        if slug == cleaned_key or map_slug_to_cleaned_key(slug) == cleaned_key:
            return slug
    return cleaned_key


def get_valid_zone_slugs() -> set[str]:
    """Return public and cleaned subdivision slugs accepted for internal citations."""
    slugs: set[str] = set()
    for zone in get_all_zones():
        slug = zone.get("slug", "")
        if slug:
            slugs.add(slug)
            slugs.add(map_slug_to_cleaned_key(slug))
            if not slug.endswith("-vinhomes"):
                slugs.add(f"{slug}-vinhomes")
    slugs.update(load_cleaned_zones_data().keys())
    slugs.update(f"{slug}-vinhomes" for slug in load_cleaned_zones_data())
    return slugs


def get_cleaned_zone_by_slug(slug: str) -> dict | None:
    """Return detailed cleaned data for a zone slug."""
    cleaned_data = load_cleaned_zones_data()
    key = map_slug_to_cleaned_key(slug)
    return cleaned_data.get(key)


def get_all_zones() -> list[dict]:
    """Return all normalized zones."""
    return load_seed_data().get("zones", [])


def get_zone_by_slug(slug: str) -> dict | None:
    """Find a normalized zone by slug."""
    mapped_slug = map_slug_to_cleaned_key(slug)
    for zone in get_all_zones():
        if zone.get("slug") in (slug, mapped_slug):
            return zone
    return None


def get_buildings_for_zone(zone_slug: str) -> list[dict]:
    """Return buildings for a zone."""
    buildings = load_seed_data().get("buildings", [])
    return [building for building in buildings if building.get("zone_slug") == zone_slug]


def get_amenities(zone_slug: str | None = None) -> list[dict]:
    """Return amenities, optionally filtered by zone."""
    amenities = load_seed_data().get("amenities", [])
    if zone_slug:
        mapped_slug = map_slug_to_cleaned_key(zone_slug)
        return [
            amenity
            for amenity in amenities
            if amenity.get("scope") == "project" or amenity.get("zone_slug") in (zone_slug, mapped_slug)
        ]
    return amenities


def get_transport_routes() -> list[dict]:
    return load_seed_data().get("transport_routes", [])


def get_matching_rules() -> dict:
    return load_seed_data().get("matching_rules", {})


def get_project_info() -> dict:
    return load_seed_data().get("project", PROJECT_OVERVIEW) or PROJECT_OVERVIEW


def format_zones_for_context(zones: list[dict]) -> str:
    """Convert normalized zones to rich context text for the LLM prompt."""
    if not zones:
        return "Không có thông tin phân khu phù hợp."

    lines = []
    for zone in zones:
        price = zone.get("total_price_range_billion", {})
        specs = zone.get("apartment_specs", {})
        spec_lines = [
            (
                f"  - {unit_type}: diện tích {spec.get('area', 'Chưa cập nhật')}, "
                f"giá {spec.get('price', 'Chưa cập nhật')}"
            )
            for unit_type, spec in specs.items()
        ]

        internal_amenities = zone.get("internal_amenities", [])[:4]
        external_amenities = zone.get("external_amenities", [])[:4]
        policies = zone.get("sales_policies", [])[:3]

        zone_lines = [
            f"### {zone.get('name', '')} (slug: {zone.get('slug', '')})",
            f"- Trạng thái bàn giao: {zone.get('handover_status') or 'Chưa cập nhật'}",
            f"- Tiêu chuẩn bàn giao: {zone.get('handover_standard') or 'Chưa cập nhật'}",
            f"- Pháp lý: {zone.get('legal_status') or 'Chưa cập nhật'}",
            f"- Vị trí: {zone.get('location_in_project') or 'Chưa cập nhật'}",
            f"- Giá tổng quan: {format_price_range(price)}",
            f"- Giới thiệu: {zone.get('description', '')[:500]}",
        ]

        if spec_lines:
            zone_lines.append("- Loại căn và giá tham khảo:\n" + "\n".join(spec_lines))
        if internal_amenities:
            zone_lines.append("- Tiện ích nội khu: " + "; ".join(internal_amenities))
        if external_amenities:
            zone_lines.append("- Tiện ích/kết nối ngoại khu: " + "; ".join(external_amenities))
        if policies:
            zone_lines.append("- Chính sách bán hàng nổi bật: " + "; ".join(policies))

        lines.append("\n".join(zone_lines))

    return "\n\n".join(lines)

