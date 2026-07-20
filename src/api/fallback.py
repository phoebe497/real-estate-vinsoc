"""Fallback rules CRUD (BAN_THIET_KE_V2 Mục 12). Cần quyền `fallback.manage`."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.dependencies import require_permission
from src.db.session import get_db
from src.models.entities import FallbackRule, User
from src.models.schemas import FallbackRuleRequest, FallbackRuleResponse

router = APIRouter(prefix="/fallback-rules", tags=["fallback-rules"])


@router.get("", response_model=list[FallbackRuleResponse])
def list_rules(
    _: User = Depends(require_permission("fallback.manage")), db: Session = Depends(get_db)
) -> list[FallbackRule]:
    return list(
        db.scalars(select(FallbackRule).order_by(FallbackRule.priority.desc(), FallbackRule.keyword)).all()
    )


@router.post("", response_model=FallbackRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    request: FallbackRuleRequest,
    _: User = Depends(require_permission("fallback.manage")),
    db: Session = Depends(get_db),
) -> FallbackRule:
    keyword = request.keyword.strip()
    if db.scalar(select(FallbackRule.id).where(FallbackRule.keyword == keyword)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Keyword đã tồn tại")
    rule = FallbackRule(
        keyword=keyword,
        response_message=request.response_message,
        priority=request.priority,
        is_active=request.is_active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/{rule_id}", response_model=FallbackRuleResponse)
def update_rule(
    rule_id: int,
    request: FallbackRuleRequest,
    _: User = Depends(require_permission("fallback.manage")),
    db: Session = Depends(get_db),
) -> FallbackRule:
    rule = db.get(FallbackRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy rule")
    keyword = request.keyword.strip()
    duplicate = db.scalar(
        select(FallbackRule.id).where(FallbackRule.keyword == keyword, FallbackRule.id != rule_id)
    )
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Keyword đã tồn tại")
    rule.keyword = keyword
    rule.response_message = request.response_message
    rule.priority = request.priority
    rule.is_active = request.is_active
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    _: User = Depends(require_permission("fallback.manage")),
    db: Session = Depends(get_db),
) -> None:
    rule = db.get(FallbackRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy rule")
    db.delete(rule)
    db.commit()
