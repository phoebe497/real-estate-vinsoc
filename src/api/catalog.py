from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from src.db.session import get_db
from src.models.entities import ApartmentSpec, Subdivision
from src.models.schemas import SubdivisionDetailResponse, SubdivisionSummaryResponse

router = APIRouter(prefix="/subdivisions", tags=["subdivisions"])


@router.get("", response_model=list[SubdivisionSummaryResponse])
def list_subdivisions(
    handover_status: str | None = None,
    unit_type: str | None = None,
    max_price: Decimal | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
) -> list[Subdivision]:
    query: Select[tuple[Subdivision]] = select(Subdivision).where(Subdivision.is_published.is_(True))
    if handover_status:
        query = query.where(Subdivision.handover_status == handover_status)
    if unit_type or max_price is not None:
        query = query.join(Subdivision.apartment_specs)
    if unit_type:
        query = query.where(ApartmentSpec.unit_type == unit_type)
    if max_price is not None:
        query = query.where(ApartmentSpec.price_min <= max_price)
    query = query.distinct().order_by(Subdivision.display_order, Subdivision.name)
    return list(db.scalars(query).all())


@router.get("/{slug}", response_model=SubdivisionDetailResponse)
def get_subdivision(slug: str, db: Session = Depends(get_db)) -> Subdivision:
    query = (
        select(Subdivision)
        .where(Subdivision.slug == slug, Subdivision.is_published.is_(True))
        .options(
            selectinload(Subdivision.apartment_specs),
            selectinload(Subdivision.amenities),
            selectinload(Subdivision.sales_policies),
        )
    )
    subdivision = db.scalar(query)
    if subdivision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phân khu")
    return subdivision
