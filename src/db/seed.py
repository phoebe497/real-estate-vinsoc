import json
import re
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.models.entities import Amenity, ApartmentSpec, SalesPolicy, Subdivision

CATALOG_PATH = Path(__file__).resolve().parents[2] / "cleaned_data" / "cleaned_apartment_zones.json"


def _numbers(value: str) -> list[Decimal]:
    return [Decimal(match.replace(",", ".")) for match in re.findall(r"\d+(?:[,.]\d+)?", value)]


def _range(value: str, multiplier: Decimal = Decimal("1")) -> tuple[Decimal | None, Decimal | None]:
    values = _numbers(value)
    if not values:
        return None, None
    minimum = values[0] * multiplier
    maximum = (values[1] if len(values) > 1 else values[0]) * multiplier
    return minimum, maximum


def seed_catalog(session: Session) -> int:
    """Synchronize reviewed catalog data into the database.

    The catalog is the source of truth for subdivisions until a dedicated CMS
    exists. The seeder intentionally upserts subdivisions and replaces child
    rows for specs, amenities and policies so local/staging/prod databases do
    not stay stale after `cleaned_data` changes.
    """
    if not CATALOG_PATH.exists():
        return 0

    payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    for order, (slug, item) in enumerate(payload.items(), start=1):
        subdivision = session.scalar(select(Subdivision).where(Subdivision.slug == slug))
        if subdivision is None:
            subdivision = Subdivision(slug=slug)
            session.add(subdivision)

        subdivision.name = item["name"][:255]
        subdivision.introduction = item.get("introduction") or "Đang cập nhật"
        subdivision.location = item.get("location") or "Đang cập nhật"
        # Cột giới hạn 255 ký tự; dữ liệu crawl đôi khi chứa mô tả dài
        subdivision.handover_status = (item.get("handover_status") or "Đang cập nhật")[:255]
        subdivision.display_order = order
        subdivision.is_published = True
        session.flush()

        session.execute(delete(ApartmentSpec).where(ApartmentSpec.subdivision_id == subdivision.id))
        session.execute(delete(Amenity).where(Amenity.subdivision_id == subdivision.id))
        session.execute(delete(SalesPolicy).where(SalesPolicy.subdivision_id == subdivision.id))

        specs = []
        for unit_type, spec in item.get("apartment_specs", {}).items():
            area_min, area_max = _range(spec.get("area", ""))
            price_min, price_max = _range(spec.get("price", ""), Decimal("1000000000"))
            specs.append(
                ApartmentSpec(
                    subdivision_id=subdivision.id,
                    unit_type=unit_type,
                    area_min=area_min,
                    area_max=area_max,
                    area_note=spec.get("area"),
                    price_min=price_min,
                    price_max=price_max,
                    price_note=spec.get("price"),
                )
            )
        session.add_all(specs)

        amenities = []
        for scope, source_key in (("internal", "internal_amenities"), ("external", "external_amenities")):
            for description in item.get(source_key, []):
                amenities.append(
                    Amenity(
                        subdivision_id=subdivision.id,
                        name=description[:255],
                        scope=scope,
                        description=description,
                    )
                )
        session.add_all(amenities)

        policies = [
            SalesPolicy(subdivision_id=subdivision.id, policy_content=content)
            for content in item.get("sales_policies", [])
        ]
        session.add_all(policies)

    session.commit()
    return len(payload)
