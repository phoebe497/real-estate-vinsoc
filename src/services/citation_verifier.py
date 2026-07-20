"""Deterministic citation verification and trusted link rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.services.retrieval import PRICE_DOMAINS, RetrievedChunk, _is_stale_period
from src.services.vinhomes_data import get_valid_zone_slugs

CITATION_TOKEN_RE = re.compile(r"\[(C\d+)\]")
INTERNAL_LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\(/phan-khu/(?P<slug>[a-z0-9\-]+)\)")
MONEY_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:ty|tỷ|trieu|triệu|%|vnd|vnđ|gtch)", re.IGNORECASE)


@dataclass
class CitationVerifierResult:
    response_text: str
    citations: list[dict[str, Any]]
    status: str = "ok"
    rejected_tokens: list[str] = field(default_factory=list)
    unused_tokens: list[str] = field(default_factory=list)
    fabricated_links: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_debug_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "accepted_citation_count": len(self.citations),
            "rejected_tokens": self.rejected_tokens,
            "unused_tokens": self.unused_tokens,
            "fabricated_links": self.fabricated_links,
            "warnings": self.warnings,
        }


def citation_from_chunk(chunk: RetrievedChunk) -> dict[str, Any]:
    return {
        "citation_id": chunk.citation_token,
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "title": chunk.title,
        "source_url": chunk.source_url,
        "source_type": chunk.source_type,
        "domain": chunk.domain,
        "confidence_level": chunk.confidence_level,
        "data_period": chunk.data_period,
        "relevance_score": round(chunk.relevance_score, 6),
        # Backward-compatible fields kept for existing FE/tests.
        "source_id": chunk.chunk_id,
        "snippet": _snippet(chunk.content),
    }


def verify_and_render_citations(response_text: str, chunks: list[RetrievedChunk]) -> CitationVerifierResult:
    token_map = {chunk.citation_token: chunk for chunk in chunks if chunk.citation_token}
    valid_slugs = get_valid_zone_slugs()
    fabricated_links: list[str] = []

    def remove_fabricated_link(match: re.Match[str]) -> str:
        slug = match.group("slug")
        fabricated_links.append(slug)
        return match.group("label")

    sanitized = INTERNAL_LINK_RE.sub(remove_fabricated_link, response_text)
    referenced_tokens = CITATION_TOKEN_RE.findall(sanitized)
    accepted_tokens: list[str] = []
    rejected_tokens: list[str] = []
    citations: list[dict[str, Any]] = []
    display_ids: dict[str, str] = {}

    for token in referenced_tokens:
        chunk = token_map.get(token)
        if not chunk:
            rejected_tokens.append(token)
            continue
        if not _trusted_source_url(chunk.source_url, valid_slugs):
            rejected_tokens.append(token)
            continue
        if _is_expired_policy(chunk):
            rejected_tokens.append(token)
            continue
        if token not in accepted_tokens:
            accepted_tokens.append(token)
            display_ids[token] = str(len(accepted_tokens))
            citation = citation_from_chunk(chunk)
            citation["citation_id"] = display_ids[token]
            citations.append(citation)

    def render_token(match: re.Match[str]) -> str:
        token = match.group(1)
        chunk = token_map.get(token)
        if token not in accepted_tokens or not chunk:
            return ""
        return f"[{display_ids[token]}]({chunk.source_url})"

    rendered = CITATION_TOKEN_RE.sub(render_token, sanitized)
    rendered = re.sub(r"\s{2,}", " ", rendered).strip()
    unused_tokens = sorted(set(token_map) - set(accepted_tokens))

    warnings: list[str] = []
    status = "ok"
    if fabricated_links:
        warnings.append("fabricated_links_removed")
    if rejected_tokens:
        warnings.append("invalid_citation_tokens_removed")
    if any(citation.get("data_period") and _is_stale_period(citation["data_period"]) for citation in citations):
        warnings.append("stale_data_warning")
        rendered = "[LƯU Ý]: Một số dữ liệu được trích dẫn có thể đã cũ, vui lòng xác nhận lại với Sales.\n\n" + rendered

    has_money = MONEY_RE.search(rendered) is not None
    has_price_citation = any(citation.get("domain") in PRICE_DOMAINS for citation in citations)
    if has_money and not has_price_citation:
        status = "insufficient_context"
        warnings.append("price_answer_missing_price_citation")

    return CitationVerifierResult(
        response_text=rendered,
        citations=citations,
        status=status,
        rejected_tokens=sorted(set(rejected_tokens)),
        unused_tokens=unused_tokens,
        fabricated_links=sorted(set(fabricated_links)),
        warnings=warnings,
    )


def _trusted_source_url(source_url: str, valid_slugs: set[str]) -> bool:
    if not source_url:
        return False
    match = re.fullmatch(r"/phan-khu/([a-z0-9\-]+)", source_url)
    if match:
        return match.group(1) in valid_slugs
    return source_url.startswith("https://")


def _is_expired_policy(chunk: RetrievedChunk) -> bool:
    if chunk.domain not in {"payment_policy", "sales_policy"}:
        return False
    period = f"{chunk.data_period} {chunk.debug.get('effective_to', '')}".lower()
    return any(marker in period for marker in ("expired", "het hieu luc", "hết hiệu lực"))


def _snippet(text: str, max_length: int = 220) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."
