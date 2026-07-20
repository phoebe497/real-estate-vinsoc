"""Subdivision recommendation service based on cleaned Vinhomes data."""

from __future__ import annotations

from src.services.vinhomes_data import (
    format_price_range,
    get_all_zones,
    get_matching_rules,
)


def _price_range_for_user_unit(zone: dict, unit_type: str | None) -> dict:
    if unit_type:
        for available_unit, spec in zone.get("apartment_specs", {}).items():
            if unit_type == available_unit or unit_type.replace("+", "") == available_unit.replace("+", ""):
                return spec.get("price_range_billion", {}) or {}
    return zone.get("total_price_range_billion", {}) or {}


def _is_handed_over(status: str | None) -> bool:
    normalized = (status or "").lower()
    return "đã" in normalized or "da" in normalized or normalized == "handed_over"


def score_zone(zone: dict, user_profile: dict, rules: dict) -> tuple[float, str]:
    """Score one subdivision against budget, unit type and purpose."""
    score = 0.0
    reasons: list[str] = []

    budget: int | None = user_profile.get("budget")
    purpose: str | None = user_profile.get("purpose")
    unit_type: str | None = user_profile.get("unit_type")

    zone_slug = zone.get("slug", "")
    price_range = _price_range_for_user_unit(zone, unit_type)
    zone_budget_fit = rules.get("zone_budget_fit", {}).get(zone_slug, {})

    if budget:
        budget_billion = budget / 1_000_000_000
        min_price = price_range.get("min")
        max_price = price_range.get("max")

        if min_price is not None and max_price is not None:
            sweet_spot = zone_budget_fit.get("sweet_spot_billion", (min_price + max_price) / 2)
            if min_price <= budget_billion <= max_price:
                score += 35
                reasons.append(
                    f"Ngân sách ~{budget_billion:.1f} tỷ phù hợp tốt, "
                    f"nằm trong khoảng {format_price_range(price_range)}"
                )
            elif budget_billion >= min_price:
                score += 20
                reasons.append(f"Ngân sách đạt ngưỡng tối thiểu {format_price_range(price_range)}")
            else:
                score -= 20

            if abs(budget_billion - sweet_spot) <= 0.5:
                score += 20
                reasons.append(f"Ngân sách gần vùng giá trung tâm khoảng {sweet_spot:.1f} tỷ")
        else:
            # Khách đã đưa ngân sách nhưng phân khu không có giá xác thực cho loại căn
            # này (chưa cập nhật/đã bán hết) → xếp sau các phân khu có giá thật.
            score -= 15
            reasons.append("Giá phân khu/loại căn này hiện chưa cập nhật đầy đủ")

    if purpose:
        purpose_zones: list[str] = rules.get("purpose_zone_affinity", {}).get(purpose, [])
        if zone_slug in purpose_zones:
            pos = purpose_zones.index(zone_slug)
            score += max(30 - pos * 8, 10)
            reasons.append(f"Phù hợp với mục đích '{purpose}'")

    if unit_type:
        available_types: list[str] = zone.get("unit_types", [])
        if unit_type in available_types or any(
            unit_type.replace("+", "") == available_type.replace("+", "")
            for available_type in available_types
        ):
            score += 15
            reasons.append(f"Có thông tin loại căn {unit_type}")

    if _is_handed_over(zone.get("handover_status")):
        score += 5
        reasons.append("Đã bàn giao")

    match_reason = " | ".join(reasons) if reasons else "Phân khu phổ biến tại Ocean Park"
    return score, match_reason


def get_zone_recommendations(
    budget: int | None = None,
    unit_type: str | None = None,
    purpose: str | None = None,
    top_k: int = 3,
) -> list[dict]:
    """Return top subdivision recommendations sorted by relevance score."""
    user_profile = {
        "budget": budget,
        "unit_type": unit_type,
        "purpose": purpose,
    }

    all_zones = get_all_zones()
    rules = get_matching_rules()

    scored: list[tuple[float, dict, str]] = []
    for zone in all_zones:
        score, reason = score_zone(zone, user_profile, rules)
        scored.append((score, zone, reason))

    scored.sort(key=lambda item: item[0], reverse=True)

    results = []
    for score, zone, reason in scored[:top_k]:
        price_range = _price_range_for_user_unit(zone, unit_type)
        results.append({
            "name": zone["name"],
            "slug": zone["slug"],
            "match_reason": reason,
            "price_range": format_price_range(price_range),
            "design_style": zone.get("design_style", ""),
            "score": round(score, 1),
            "unit_types": zone.get("unit_types", []),
            "target_audience": zone.get("target_audience", []),
            "handover_status": zone.get("handover_status", ""),
        })

    return results
