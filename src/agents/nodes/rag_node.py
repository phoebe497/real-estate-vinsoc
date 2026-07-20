"""RAG Node — Retrieval-Augmented Generation context builder.

Node này tìm kiếm dữ liệu phân khu phù hợp với user profile
và chuẩn bị context text để đưa vào LLM prompt.

Đây là "RAG đơn giản" không dùng vector DB — chỉ filter/score
trực tiếp từ JSON seed data. ChromaDB có thể được thêm vào sau.
"""

from __future__ import annotations

import logging

from src.agents.state import AgentState, Citation, ZoneMatch, get_last_user_message
from src.config import get_settings
from src.services.citation_verifier import citation_from_chunk
from src.services.embeddings import try_embed_query
from src.services.retrieval import build_retrieval_query, get_retriever, normalize_query
from src.services.vinhomes_data import (
    format_zones_for_context,
    get_all_zones,
    get_amenities,
    get_matching_rules,
    get_project_info,
    get_transport_routes,
    get_zone_by_slug,
)

TOP_ZONE_COUNT = 3  # Số phân khu gợi ý tối đa trả về
TOP_CHUNK_COUNT = 5


def _price_range_for_user_unit(zone: dict, unit_type: str | None) -> dict:
    """Prefer the requested apartment type price range; fallback to total range."""
    if unit_type:
        specs = zone.get("apartment_specs", {})
        for available_unit, spec in specs.items():
            if unit_type == available_unit or unit_type.replace("+", "") == available_unit.replace("+", ""):
                return spec.get("price_range_billion", {}) or {}
    return zone.get("total_price_range_billion", {}) or {}


def _candidate_unit_types(user_profile: dict) -> list[str]:
    unit_type = user_profile.get("unit_type")
    if unit_type:
        return [unit_type]
    family_size = user_profile.get("family_size") or 0
    if family_size >= 4:
        return ["2PN+1", "3PN", "2PN"]
    if family_size >= 3:
        return ["2PN", "2PN+1"]
    return []


def _price_range_for_profile(zone: dict, user_profile: dict) -> dict:
    candidate_units = _candidate_unit_types(user_profile)
    if not candidate_units:
        return zone.get("total_price_range_billion", {}) or {}

    ranges = []
    specs = zone.get("apartment_specs", {})
    for candidate in candidate_units:
        for available_unit, spec in specs.items():
            if candidate == available_unit or candidate.replace("+", "") == available_unit.replace("+", ""):
                price_range = spec.get("price_range_billion", {}) or {}
                if price_range:
                    ranges.append(price_range)

    if not ranges:
        return {}
    return {
        "min": min(item["min"] for item in ranges),
        "max": max(item["max"] for item in ranges),
    }


def _format_billion(value: float | int | None) -> str:
    if value is None:
        return "?"
    text = f"{float(value):.1f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def _format_price_range(price_range: dict) -> str:
    if not price_range:
        return ""
    return f"{_format_billion(price_range.get('min'))} - {_format_billion(price_range.get('max'))} tỷ"


def _legacy_public_slug(slug: str) -> str:
    if not slug:
        return ""
    return slug if slug.endswith("-vinhomes") else f"{slug}-vinhomes"


def _has_profile_preferences(user_profile: dict) -> bool:
    return any(
        user_profile.get(key)
        for key in ("budget", "unit_type", "purpose", "timeline", "family_size")
    )


def _snippet(text: str, max_length: int = 220) -> str:
    """Return a compact one-line snippet for citations."""
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."


def _zone_citation(zone: dict) -> Citation:
    slug = zone.get("slug", "")
    return Citation(
        source_type="zone",
        source_id=slug,
        source_url=f"/phan-khu/{slug}" if slug else "",
        title=zone.get("name", slug),
        snippet=_snippet(zone.get("description", "")),
        confidence_level=zone.get("confidence_level", "medium"),
    )


def _chunk_citation(chunk: dict) -> Citation:
    public_slug = chunk.get("public_slug") or chunk.get("subdivision_slug", "")
    topic = chunk.get("topic", "general")
    title = f"{chunk.get('subdivision_name', public_slug)} - {topic}"
    return Citation(
        source_type="knowledge_chunk",
        source_id=chunk.get("chunk_id", f"{public_slug}:{topic}"),
        source_url=f"/phan-khu/{public_slug}" if public_slug else "",
        title=title,
        snippet=_snippet(chunk.get("content", "")),
        confidence_level=chunk.get("confidence_level", "medium"),
    )


def _retrieved_chunk_citation(chunk) -> Citation:
    return Citation(**citation_from_chunk(chunk))


def _chunk_match_reason(domain: str, normalized_query: str) -> str:
    if domain == "amenities":
        if any(term in normalized_query for term in ("truong", "vinschool", "vinuni", "brighton", "con nho", "tre em")):
            return "Có thông tin tiện ích giáo dục và sinh hoạt gia đình phù hợp nhu cầu"
        if any(term in normalized_query for term in ("ho", "bien", "crystal", "ngoc trai")):
            return "Có dữ liệu tiện ích hồ, cảnh quan và điểm vui chơi trong đại đô thị"
        return "Có dữ liệu tiện ích liên quan trực tiếp đến câu hỏi"
    if domain == "location":
        return "Phù hợp nhờ thông tin vị trí và kết nối di chuyển"
    if domain == "price":
        return "Có dữ liệu giá tham khảo phù hợp để so sánh ban đầu"
    if domain == "progress":
        return "Có dữ liệu tiến độ và tình trạng bàn giao để cân nhắc thời điểm ở"
    return "Có thông tin phù hợp với nhu cầu tư vấn"


def _zones_from_retrieved_chunks(
    chunks,
    normalized_query: str,
    unit_type: str | None = None,
) -> tuple[list[ZoneMatch], list[dict]]:
    """Build UI zone cards from the same trusted chunks used for generation."""
    zones: list[ZoneMatch] = []
    matched: list[dict] = []
    seen: set[str] = set()

    for chunk in chunks:
        slug = getattr(chunk, "zone_slug", None)
        if not slug or slug in seen:
            continue

        zone = get_zone_by_slug(slug)
        if not zone:
            continue

        seen.add(slug)
        matched.append(zone)
        price_range = _price_range_for_user_unit(zone, unit_type)
        zones.append(
            ZoneMatch(
                name=zone.get("name", slug),
                slug=_legacy_public_slug(slug),
                match_reason=_chunk_match_reason(getattr(chunk, "domain", "general"), normalized_query),
                price_range=_format_price_range(price_range),
                design_style=zone.get("design_style", ""),
            )
        )

        if len(zones) >= TOP_ZONE_COUNT:
            break

    return zones, matched


def _score_zone(zone: dict, user_profile: dict, rules: dict) -> tuple[float, str]:
    """Tính điểm phù hợp của phân khu với user profile.

    Trả về (score, match_reason).
    Score cao hơn = phù hợp hơn.
    """
    score = 0.0
    reasons = []

    budget = user_profile.get("budget")
    purpose = user_profile.get("purpose")
    unit_type = user_profile.get("unit_type")
    unit_type_aliases = {
        "1PN": ("1PN", "1 ngủ"),
        "1PN+": ("1PN+", "1 ngủ + 1"),
        "2PN": ("2PN", "2 ngủ"),
        "2PN+": ("2PN+", "2 ngủ + 1"),
        "3PN": ("3PN", "3 ngủ"),
        "Studio": ("Studio",),
    }

    price_range = _price_range_for_profile(zone, user_profile)
    zone_slug = zone.get("slug", "")
    zone_budget_fit = rules.get("zone_budget_fit", {}).get(zone_slug, {})

    # --- Budget scoring ---
    if budget:
        budget_billion = budget / 1_000_000_000
        min_price = price_range.get("min", 0)
        sweet_spot = zone_budget_fit.get("sweet_spot_billion", min_price)

        if price_range and budget_billion >= min_price:
            score += 30
            max_price = price_range.get("max")
            if max_price and budget_billion <= max_price + 0.3:
                score += 15
                reasons.append(
                    f"Ngân sách ~{budget_billion:.1f} tỷ khớp với khoảng giá căn phù hợp "
                    f"({min_price}-{max_price} tỷ)"
                )
            elif abs(budget_billion - sweet_spot) <= 1.0:
                score += 20
                reasons.append(
                    f"Ngân sách ~{budget_billion:.1f} tỷ phù hợp tốt "
                    f"(ngưỡng lý tưởng {sweet_spot:.1f} tỷ)"
                )
            else:
                reasons.append(
                    f"Ngân sách {budget_billion:.1f} tỷ nằm trong khoảng "
                    f"{min_price}-{price_range.get('max', '?')} tỷ"
                )
        else:
            # Ngân sách chưa đủ
            score -= 20

    # --- Purpose affinity ---
    if purpose:
        purpose_zones = rules.get("purpose_zone_affinity", {}).get(purpose, [])
        if zone_slug in purpose_zones:
            pos = purpose_zones.index(zone_slug)
            score += max(30 - pos * 8, 10)
            reasons.append(f"Phù hợp với mục đích '{purpose}'")

    # --- Unit type availability ---
    if unit_type:
        available_types = zone.get("unit_types", [])
        requested_types = unit_type_aliases.get(unit_type, (unit_type,))
        if unit_type in available_types or any(
            requested.replace("+", "") in t.replace("+", "")
            for requested in requested_types
            for t in available_types
        ):
            score += 15
            reasons.append(f"Có sẵn loại căn {unit_type}")

    family_size = user_profile.get("family_size") or 0
    if family_size >= 4:
        available_types = zone.get("unit_types", [])
        if any(unit in available_types for unit in ("2PN", "2PN+1", "3PN")):
            score += 12
            reasons.append("Có lựa chọn 2PN/2PN+/3PN phù hợp gia đình 4 người")

    if user_profile.get("school_need"):
        amenities_text = " ".join(zone.get("external_amenities", []) + zone.get("internal_amenities", [])).lower()
        if any(term in amenities_text for term in ("vinschool", "trường", "brighton", "deway", "học")):
            score += 12
            reasons.append("Có tiện ích giáo dục/trường học phù hợp gia đình có con")

    # --- Handover status bonus ---
    if zone.get("handover_status") == "handed_over":
        score += 5
        reasons.append("Đã bàn giao")

    match_reason = " | ".join(reasons) if reasons else "Phân khu phổ biến tại Ocean Park"
    return score, match_reason


async def rag_node(state: AgentState) -> dict:
    """LangGraph node: tìm context phù hợp và gợi ý phân khu."""
    intent = state.get("intent", "consult")
    user_profile = state.get("user_profile", {})
    messages = state.get("messages", [])

    # Lấy câu hỏi cuối của user
    last_user_msg = get_last_user_message(messages)
    normalized_last_user_msg = normalize_query(last_user_msg)
    base_retrieval_query = build_retrieval_query(last_user_msg, intent=intent)
    explicit_zone_slugs = set(base_retrieval_query.zone_slugs)

    # --- Build project overview context ---
    project = get_project_info()
    project_context = (
        f"**Dự án:** {project.get('name')}\n"
        f"**Vị trí:** {project.get('location')}\n"
        f"**Mô tả:** {project.get('description')}\n"
        f"**Điểm nổi bật:** {', '.join(project.get('highlights', []))}"
    )

    # --- Zone matching & context ---
    all_zones = get_all_zones()
    rules = get_matching_rules()
    recommended_zones: list[ZoneMatch] = []
    citations: list[Citation] = []
    matched_zones: list[dict] = []

    if explicit_zone_slugs:
        matched_zones = [
            zone for zone in all_zones
            if zone.get("slug") in explicit_zone_slugs
        ][:TOP_ZONE_COUNT]
        recommended_zones = []
        for zone in matched_zones:
            price_range = _price_range_for_user_unit(zone, user_profile.get("unit_type"))
            recommended_zones.append(
                ZoneMatch(
                    name=zone.get("name", zone.get("slug", "")),
                    slug=(
                        _legacy_public_slug(zone.get("slug", ""))
                        if get_settings().rag_provider == "pgvector"
                        else zone.get("slug", "")
                    ),
                    match_reason="Đúng phân khu anh/chị đang hỏi, có thể mở nhanh để xem chi tiết.",
                    price_range=_format_price_range(price_range),
                    design_style=zone.get("design_style", ""),
                )
            )
        citations.extend(_zone_citation(z) for z in matched_zones)
        zone_context = (
            f"**Thông tin dự án:**\n{project_context}\n\n"
            f"**Phân khu đang được hỏi:**\n"
            f"{format_zones_for_context(matched_zones)}"
        )
    elif _has_profile_preferences(user_profile) and intent in ("zone_match", "consult", "price_query"):
        # Score và sort zones
        scored = []
        for zone in all_zones:
            score, reason = _score_zone(zone, user_profile, rules)
            scored.append((score, zone, reason))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Top phân khu phù hợp nhất
        top_zones = scored[:TOP_ZONE_COUNT]
        matched_zones = [z for _, z, _ in top_zones]
        recommended_zones = [
            ZoneMatch(
                name=z["name"],
                slug=z["slug"],
                match_reason=reason,
                price_range=_format_price_range(_price_range_for_profile(z, user_profile)),
                design_style=z.get("design_style", ""),
            )
            for score, z, reason in top_zones
            if score >= 0  # Chỉ lấy zones có score dương
        ]

        citations.extend(_zone_citation(z) for z in matched_zones)

        zone_context = (
            f"**Thông tin dự án:**\n{project_context}\n\n"
            f"**Các phân khu phù hợp:**\n"
            f"{format_zones_for_context(matched_zones)}"
        )
    else:
        zone_context = f"**Thông tin dự án:**\n{project_context}"

    # --- Amenities context (nếu hỏi về tiện ích/vị trí) ---
    amenity_keywords = [
        "tien ich",
        "truong",
        "benh vien",
        "shopping",
        "di dau",
        "gan",
        "ho",
        "vincom",
        "vinuni",
        "vinschool",
        "tre em",
        "con nho",
    ]
    query_embedding = None
    if get_settings().rag_provider == "pgvector":
        query_embedding = await try_embed_query(last_user_msg)

    retrieval_query = build_retrieval_query(
        last_user_msg,
        intent=intent,
        zone_slugs=[z.get("slug", "") for z in matched_zones],
        top_k=TOP_CHUNK_COUNT,
        query_embedding=query_embedding,
    )
    retrieval_result = await get_retriever().retrieve(retrieval_query)
    knowledge_chunks = retrieval_result.chunks
    if knowledge_chunks:
        zone_context += "\n\n**Knowledge chunks bổ sung:**\n" + retrieval_result.context
        citations.extend(_retrieved_chunk_citation(chunk) for chunk in knowledge_chunks)

        retrieval_zones, retrieval_matched_zones = _zones_from_retrieved_chunks(
            knowledge_chunks,
            normalized_last_user_msg,
            user_profile.get("unit_type"),
        )
        if retrieval_zones and not user_profile.get("budget") and not explicit_zone_slugs:
            recommended_zones = retrieval_zones
            matched_zones = retrieval_matched_zones

    if any(kw in normalized_last_user_msg for kw in amenity_keywords):
        amenities = get_amenities()[:5]  # Top 5 tiện ích
        amenity_lines = [
            f"- {a['name']} ({a['type']}): {a.get('description', '')} — {a.get('distance_text', '')}"
            for a in amenities
        ]
        zone_context += "\n\n**Tiện ích nổi bật:**\n" + "\n".join(amenity_lines)

    # --- Transport context (nếu hỏi về đường đi) ---
    transport_keywords = ["di tu", "mat bao lau", "xa khong", "khoang cach", "cau", "di chuyen"]
    if any(kw in normalized_last_user_msg for kw in transport_keywords):
        routes = get_transport_routes()
        route_lines = [
            f"- Từ {r['origin']}: {r['distance_km']}km, {r['driving_time_min']}-{r['driving_time_max']} phút"
            for r in routes
        ]
        zone_context += "\n\n**Đường đi tham khảo:**\n" + "\n".join(route_lines)

    has_project_context = bool(project_context.strip())
    has_retrieval_context = bool(
        knowledge_chunks
        or matched_zones
        or (intent in {"consult", "zone_match", "price_query"} and has_project_context)
    )

    status = "ok" if has_retrieval_context else "insufficient_context"
    logging.getLogger("agent.rag_node").info(
        "[rag_node] session=%s intent=%s status=%s chunks=%d zones=%d citations=%d "
        "context_chars=%d matched_zones=%s query=%r",
        state.get("session_id", "?"),
        intent,
        status,
        len(knowledge_chunks),
        len(recommended_zones),
        len(citations),
        len(zone_context),
        [z.get("slug") for z in (matched_zones or [])][:3],
        last_user_msg[:100],
    )
    return {
        "zone_context": zone_context,
        "recommended_zones": recommended_zones,
        "citations": citations,
        "retrieved_chunks": knowledge_chunks,
        "retrieval_debug": retrieval_result.debug,
        "status": status,
    }
