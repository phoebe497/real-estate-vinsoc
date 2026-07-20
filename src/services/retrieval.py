"""Retriever abstraction and deterministic hybrid retrieval helpers."""

from __future__ import annotations

import logging
import math
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any, Protocol

from sqlalchemy import text

from src.config import get_settings
from src.services.vinhomes_data import (
    get_all_zones,
    load_knowledge_chunks,
    map_cleaned_key_to_seed_slug,
    map_slug_to_cleaned_key,
)

logger = logging.getLogger(__name__)

PRICE_DOMAINS = {"price", "payment_policy", "sales_policy"}


@lru_cache
def _get_async_session_factory():
    """Async session dùng riêng cho nhánh pgvector (RAG_PROVIDER=pgvector).

    Lớp async DB toàn cục đã bị gỡ (thiết kế V2 dùng SQLAlchemy sync);
    pgvector là tuỳ chọn nên engine async chỉ được tạo khi thật sự cần.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    database_url = get_settings().database_url
    if database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    engine = create_async_engine(database_url)
    return async_sessionmaker(engine, expire_on_commit=False)


@dataclass(frozen=True)
class RetrievalQuery:
    raw_query: str
    normalized_query: str = ""
    intent: str = "consult"
    domain: str = "general"
    project_slug: str | None = None
    zone_slugs: tuple[str, ...] = ()
    subzone_slugs: tuple[str, ...] = ()
    building_codes: tuple[str, ...] = ()
    top_k: int | None = None
    token_budget: int | None = None
    query_embedding: list[float] | None = None


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    title: str
    content: str
    source_url: str
    source_type: str
    domain: str
    confidence_level: str = "medium"
    data_period: str = ""
    project_slug: str | None = None
    zone_slug: str | None = None
    subzone_slug: str | None = None
    building_code: str | None = None
    vector_score: float = 0.0
    lexical_score: float = 0.0
    metadata_score: float = 0.0
    freshness_score: float = 0.0
    relevance_score: float = 0.0
    citation_token: str = ""
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk]
    context: str
    debug: dict[str, Any]


class Retriever(Protocol):
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        """Return packed context and retrieved chunks for an already built query."""


def normalize_query(query: str) -> str:
    query = query.replace("đ", "d").replace("Đ", "D")
    text_value = unicodedata.normalize("NFKD", query)
    text_value = "".join(ch for ch in text_value if not unicodedata.combining(ch))
    text_value = text_value.lower()
    text_value = re.sub(r"[^a-z0-9\s\.\-]", " ", text_value)
    return re.sub(r"\s+", " ", text_value).strip()


def classify_domain(normalized_query: str, intent: str = "consult") -> str:
    price_pattern = (
        r"\b("
        r"gia\s+(?:bao nhieu|khoang|tam|can|chot|ban|goc|tham khao)|"
        r"(?:muc|khoang|tam|tong|bang)\s+gia|"
        r"\d+(?:[\.,]\d+)?\s*(?:ty|trieu)|"
        r"vay|thanh toan|chiet khau"
        r")\b"
    )
    if intent == "price_query" or re.search(price_pattern, normalized_query):
        return "price"
    if re.search(r"\b(chinh sach|uu dai|booking|coc|vay|lai suat)\b", normalized_query):
        return "payment_policy"
    if re.search(r"\b(phap ly|so hong|so do|hop dong)\b", normalized_query):
        return "legal"
    if re.search(r"\b(tien do|ban giao|xay dung|hien trang)\b", normalized_query):
        return "progress"
    if re.search(r"\b(tien ich|vuon|ho|cong vien|truong|benh vien|vincom|vinuni|vinschool)\b", normalized_query):
        return "amenities"
    if re.search(r"\b(vi tri|duong|ket noi|di chuyen|metro|gan)\b", normalized_query):
        return "location"
    return "general"


def extract_metadata(normalized_query: str) -> dict[str, tuple[str, ...]]:
    zone_slugs: set[str] = set()
    for zone in get_all_zones():
        slug = zone.get("slug", "")
        name = normalize_query(zone.get("name", ""))
        cleaned = map_slug_to_cleaned_key(slug)
        aliases = {
            normalize_query(slug),
            normalize_query(slug.removesuffix("-vinhomes")),
            normalize_query(name),
            normalize_query(name.removesuffix(" vinhomes")),
            normalize_query(cleaned),
        }
        aliases.update(alias[4:] for alias in list(aliases) if alias.startswith("the ") and len(alias) > 6)
        if any(_contains_phrase(normalized_query, alias) for alias in aliases):
            zone_slugs.add(slug)

    building_codes = {
        match.group(0).upper()
        for match in re.finditer(r"\b[A-Z]?\d{1,2}\.\d{2}\b", normalized_query.upper())
    }
    return {
        "zone_slugs": tuple(sorted(zone_slugs)),
        "building_codes": tuple(sorted(building_codes)),
    }


def _contains_phrase(text_value: str, phrase: str) -> bool:
    if not phrase or len(phrase) < 4:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text_value) is not None


def build_retrieval_query(
    raw_query: str,
    *,
    intent: str = "consult",
    domain: str | None = None,
    zone_slugs: list[str] | tuple[str, ...] | None = None,
    top_k: int | None = None,
    token_budget: int | None = None,
    query_embedding: list[float] | None = None,
) -> RetrievalQuery:
    normalized = normalize_query(raw_query)
    metadata = extract_metadata(normalized)
    detected_zone_slugs = set(metadata["zone_slugs"])
    detected_zone_slugs.update(slug for slug in (zone_slugs or ()) if slug)
    return RetrievalQuery(
        raw_query=raw_query,
        normalized_query=normalized,
        intent=intent,
        domain=domain or classify_domain(normalized, intent),
        zone_slugs=tuple(sorted(detected_zone_slugs)),
        building_codes=metadata["building_codes"],
        top_k=top_k,
        token_budget=token_budget,
        query_embedding=query_embedding,
    )


def _terms(text_value: str) -> set[str]:
    return {term for term in normalize_query(text_value).split() if len(term) >= 3}


def _topic_to_domain(topic: str) -> str:
    topic_norm = normalize_query(topic)
    if any(key in topic_norm for key in ("apartment specs", "apartment_specs", "price", "gia")):
        return "price"
    if any(key in topic_norm for key in ("sales policies", "sales_policies", "policy", "policies", "chinh sach")):
        return "payment_policy"
    if "amenit" in topic_norm or "tien ich" in topic_norm:
        return "amenities"
    if "location" in topic_norm or "vi tri" in topic_norm:
        return "location"
    if "legal" in topic_norm:
        return "legal"
    if "progress" in topic_norm or "tien do" in topic_norm:
        return "progress"
    return "general"


def _chunk_from_json(raw: dict, index: int = 0) -> RetrievedChunk:
    subdivision_slug = str(raw.get("subdivision_slug", "")).strip()
    public_slug = raw.get("public_slug") or map_cleaned_key_to_seed_slug(subdivision_slug)
    topic = str(raw.get("topic", "general")).strip() or "general"
    chunk_id = str(raw.get("chunk_id") or f"{subdivision_slug}:{topic}")
    title = str(raw.get("title") or f"{raw.get('subdivision_name', public_slug)} - {topic}")
    domain = str(raw.get("domain") or _topic_to_domain(topic))
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=str(raw.get("document_id") or f"json:{subdivision_slug}"),
        title=title,
        content=str(raw.get("content", "")),
        source_url=str(raw.get("source_url") or (f"/phan-khu/{public_slug}" if public_slug else "")),
        source_type=str(raw.get("source_type") or "knowledge_chunk"),
        domain=domain,
        confidence_level=str(raw.get("confidence_level") or "medium"),
        data_period=str(raw.get("data_period") or ""),
        project_slug=str(raw.get("project_slug") or "vinhomes-ocean-park-gia-lam"),
        zone_slug=str(public_slug or ""),
        subzone_slug=subdivision_slug or None,
        building_code=raw.get("building_code"),
        lexical_score=float(raw.get("score", 0.0)),
        debug={"source": "legacy_json", "index": index},
    )


def _lexical_rank(chunks: list[RetrievedChunk], query: RetrievalQuery) -> list[RetrievedChunk]:
    query_terms = _terms(query.normalized_query or query.raw_query)
    ranked: list[RetrievedChunk] = []
    for chunk in chunks:
        haystack = " ".join(
            [
                chunk.chunk_id,
                chunk.title,
                chunk.domain,
                chunk.zone_slug or "",
                chunk.subzone_slug or "",
                chunk.content,
            ]
        )
        hay_terms = _terms(haystack)
        overlap = len(query_terms & hay_terms)
        phrase_bonus = 2 if query.normalized_query and query.normalized_query in normalize_query(haystack) else 0
        score = overlap + phrase_bonus
        if chunk.domain == query.domain:
            score += 1
        if query.zone_slugs and chunk.zone_slug in query.zone_slugs:
            score += 4
        if score > 0:
            copy = RetrievedChunk(**{**chunk.__dict__})
            copy.lexical_score = float(score)
            ranked.append(copy)
    ranked.sort(key=lambda item: item.lexical_score, reverse=True)
    return ranked


def reciprocal_rank_fusion(
    vector_results: list[RetrievedChunk],
    lexical_results: list[RetrievedChunk],
    query: RetrievalQuery,
) -> list[RetrievedChunk]:
    settings = get_settings()
    by_id: dict[str, RetrievedChunk] = {}
    scores: dict[str, float] = {}

    for weight, results, score_attr in (
        (settings.rag_vector_weight, vector_results, "vector_score"),
        (settings.rag_lexical_weight, lexical_results, "lexical_score"),
    ):
        for rank, chunk in enumerate(results, start=1):
            existing = by_id.setdefault(chunk.chunk_id, chunk)
            setattr(existing, score_attr, max(getattr(existing, score_attr), getattr(chunk, score_attr)))
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + weight / (settings.rag_rrf_k + rank)

    fused: list[RetrievedChunk] = []
    for chunk_id, chunk in by_id.items():
        chunk.metadata_score = _metadata_score(chunk, query)
        chunk.freshness_score = _freshness_score(chunk)
        chunk.relevance_score = min(1.0, scores[chunk_id] + chunk.metadata_score + chunk.freshness_score)
        chunk.debug.update(
            {
                "rrf_score": round(scores[chunk_id], 6),
                "vector_score": round(chunk.vector_score, 6),
                "lexical_score": round(chunk.lexical_score, 6),
                "metadata_score": round(chunk.metadata_score, 6),
                "freshness_score": round(chunk.freshness_score, 6),
                "relevance_score": round(chunk.relevance_score, 6),
            }
        )
        fused.append(chunk)
    fused.sort(key=lambda item: item.relevance_score, reverse=True)
    return fused


def _metadata_score(chunk: RetrievedChunk, query: RetrievalQuery) -> float:
    settings = get_settings()
    score = 0.0
    if query.domain != "general" and chunk.domain == query.domain:
        score += settings.rag_domain_boost
    if query.zone_slugs and chunk.zone_slug in query.zone_slugs:
        score += settings.rag_metadata_boost
    if query.building_codes and chunk.building_code in query.building_codes:
        score += settings.rag_metadata_boost
    return score


def _freshness_score(chunk: RetrievedChunk) -> float:
    if not chunk.data_period:
        return 0.0
    if _is_stale_period(chunk.data_period):
        return 0.0
    return get_settings().rag_freshness_boost


def _is_stale_period(data_period: str) -> bool:
    match = re.search(r"(20\d{2})[-/](0?[1-9]|1[0-2])", data_period)
    if not match:
        quarter = re.search(r"Q([1-4])/(20\d{2})", data_period, re.IGNORECASE)
        if not quarter:
            return False
        month = int(quarter.group(1)) * 3
        year = int(quarter.group(2))
    else:
        year = int(match.group(1))
        month = int(match.group(2))
    now = datetime.now(UTC)
    age_months = (now.year - year) * 12 + (now.month - month)
    return age_months > get_settings().rag_stale_months


def apply_metadata_filter(chunks: list[RetrievedChunk], query: RetrievalQuery) -> list[RetrievedChunk]:
    if not query.zone_slugs and not query.building_codes:
        return chunks
    filtered: list[RetrievedChunk] = []
    for chunk in chunks:
        zone_ok = bool(query.zone_slugs and chunk.zone_slug in query.zone_slugs)
        building_ok = bool(query.building_codes and chunk.building_code in query.building_codes)
        if zone_ok or building_ok:
            filtered.append(chunk)
    return filtered or chunks


def remove_duplicate_chunks(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    selected: list[RetrievedChunk] = []
    seen_ids: set[str] = set()
    seen_signatures: set[str] = set()
    for chunk in chunks:
        if chunk.chunk_id in seen_ids:
            continue
        signature_terms = sorted(_terms(chunk.content))[:40]
        signature = " ".join(signature_terms)
        if signature and signature in seen_signatures:
            continue
        seen_ids.add(chunk.chunk_id)
        seen_signatures.add(signature)
        selected.append(chunk)
    return selected


def estimate_tokens(text_value: str) -> int:
    return max(1, math.ceil(len(text_value.split()) * 1.35))


def pack_context(chunks: list[RetrievedChunk], token_budget: int) -> tuple[str, list[RetrievedChunk], int]:
    lines: list[str] = []
    selected: list[RetrievedChunk] = []
    used_tokens = 0
    for index, chunk in enumerate(chunks, start=1):
        token = f"C{index}"
        entry = (
            f"[{token}] {chunk.title}\n"
            f"source: {chunk.chunk_id.replace(':', '/')}\n"
            f"Domain: {chunk.domain}; Confidence: {chunk.confidence_level}; "
            f"Data period: {chunk.data_period or 'unknown'}\n"
            f"{chunk.content.strip()}"
        )
        entry_tokens = estimate_tokens(entry)
        if selected and used_tokens + entry_tokens > token_budget:
            break
        chunk.citation_token = token
        selected.append(chunk)
        lines.append(entry)
        used_tokens += entry_tokens
    return "\n\n".join(lines), selected, used_tokens


class BaseHybridRetriever:
    async def _retrieve_candidates(self, query: RetrievalQuery) -> tuple[list[RetrievedChunk], list[RetrievedChunk]]:
        raise NotImplementedError

    async def _retrieve_fallback_candidates(
        self,
        query: RetrievalQuery,
    ) -> tuple[list[RetrievedChunk], list[RetrievedChunk]]:
        return [], []

    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        settings = get_settings()
        started = time.perf_counter()
        vector_started = time.perf_counter()
        vector_results, lexical_results = await self._retrieve_candidates(query)
        retrieval_ms = (time.perf_counter() - vector_started) * 1000
        fused = reciprocal_rank_fusion(vector_results, lexical_results, query)
        filtered = apply_metadata_filter(fused, query)
        deduped = remove_duplicate_chunks(filtered)
        min_score = settings.rag_min_score
        eligible = [chunk for chunk in deduped if chunk.relevance_score >= min_score]
        fallback_used = False
        if not eligible:
            fallback_vector_results, fallback_lexical_results = await self._retrieve_fallback_candidates(query)
            if fallback_vector_results or fallback_lexical_results:
                fallback_used = True
                fused = reciprocal_rank_fusion(fallback_vector_results, fallback_lexical_results, query)
                filtered = apply_metadata_filter(fused, query)
                deduped = remove_duplicate_chunks(filtered)
                eligible = [chunk for chunk in deduped if chunk.relevance_score >= min_score]
        top_k = query.top_k or settings.rag_top_k
        context, selected, context_tokens = pack_context(
            eligible[:top_k],
            query.token_budget or settings.rag_context_token_budget,
        )
        total_ms = (time.perf_counter() - started) * 1000
        debug = {
            "provider": self.__class__.__name__,
            "domain": query.domain,
            "retrieval_latency_ms": round(retrieval_ms, 2),
            "total_latency_ms": round(total_ms, 2),
            "retrieved_count": len(fused),
            "selected_chunk_count": len(selected),
            "context_token_count": context_tokens,
            "fallback_used": fallback_used,
            "score_breakdown": [
                {
                    "chunk_id": chunk.chunk_id,
                    "citation_token": chunk.citation_token,
                    **chunk.debug,
                }
                for chunk in selected
            ],
        }
        return RetrievalResult(chunks=selected, context=context, debug=debug)


class LegacyJsonRetriever(BaseHybridRetriever):
    async def _retrieve_candidates(self, query: RetrievalQuery) -> tuple[list[RetrievedChunk], list[RetrievedChunk]]:
        chunks = [_chunk_from_json(raw, index) for index, raw in enumerate(load_knowledge_chunks())]
        lexical = _lexical_rank(chunks, query)[: get_settings().rag_lexical_top_k]
        return [], lexical


class PgVectorHybridRetriever(BaseHybridRetriever):
    async def _retrieve_candidates(self, query: RetrievalQuery) -> tuple[list[RetrievedChunk], list[RetrievedChunk]]:
        vector_results = await self._vector_search(query)
        lexical_results = await self._lexical_search(query)
        return vector_results, lexical_results

    async def _retrieve_fallback_candidates(
        self,
        query: RetrievalQuery,
    ) -> tuple[list[RetrievedChunk], list[RetrievedChunk]]:
        return await LegacyJsonRetriever()._retrieve_candidates(query)

    async def _vector_search(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        settings = get_settings()
        if not query.query_embedding or not settings.database_url.startswith("postgres"):
            return []
        query_embedding = _vector_literal(query.query_embedding)
        sql = text(
            """
            SELECT id AS chunk_id, COALESCE(document_id, id) AS document_id,
                   COALESCE(title, topic, id) AS title, content,
                   COALESCE(source_url, '') AS source_url,
                   COALESCE(source_type, 'knowledge_chunk') AS source_type,
                   COALESCE(domain, topic, 'general') AS domain,
                   COALESCE(confidence_level, 'medium') AS confidence_level,
                   COALESCE(data_period, '') AS data_period,
                   project_slug, zone_slug, subzone_slug, building_code,
                   1 - (embedding <=> CAST(:query_embedding AS vector)) AS vector_score
            FROM knowledge_chunks
            WHERE COALESCE(is_active, true) = true
              AND embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:query_embedding AS vector)
            LIMIT :limit
            """
        )
        try:
            async with _get_async_session_factory()() as session:
                rows = (await session.execute(
                    sql,
                    {
                        "query_embedding": query_embedding,
                        "limit": settings.rag_vector_top_k,
                    },
                )).mappings().all()
        except Exception as exc:
            logger.warning("pgvector search failed; falling back to lexical", extra={"error_type": type(exc).__name__})
            return []
        return [_chunk_from_row(row, "pgvector") for row in rows]

    async def _lexical_search(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        settings = get_settings()
        if not settings.database_url.startswith("postgres"):
            return (await LegacyJsonRetriever()._retrieve_candidates(query))[1]
        sql = text(
            """
            SELECT id AS chunk_id, COALESCE(document_id, id) AS document_id,
                   COALESCE(title, topic, id) AS title, content,
                   COALESCE(source_url, '') AS source_url,
                   COALESCE(source_type, 'knowledge_chunk') AS source_type,
                   COALESCE(domain, topic, 'general') AS domain,
                   COALESCE(confidence_level, 'medium') AS confidence_level,
                   COALESCE(data_period, '') AS data_period,
                   project_slug, zone_slug, subzone_slug, building_code,
                   ts_rank_cd(search_vector, websearch_to_tsquery('simple', :query)) AS lexical_score
            FROM knowledge_chunks
            WHERE COALESCE(is_active, true) = true
              AND search_vector @@ websearch_to_tsquery('simple', :query)
            ORDER BY lexical_score DESC
            LIMIT :limit
            """
        )
        try:
            async with _get_async_session_factory()() as session:
                rows = (await session.execute(
                    sql,
                    {"query": query.normalized_query, "limit": settings.rag_lexical_top_k},
                )).mappings().all()
        except Exception as exc:
            logger.warning("postgres lexical search failed; falling back to legacy lexical", extra={"error_type": type(exc).__name__})
            return (await LegacyJsonRetriever()._retrieve_candidates(query))[1]
        return [_chunk_from_row(row, "postgres_fts") for row in rows]


def _chunk_from_row(row: Any, source: str) -> RetrievedChunk:
    data = dict(row)
    chunk = RetrievedChunk(
        chunk_id=str(data.get("chunk_id", "")),
        document_id=str(data.get("document_id", "")),
        title=str(data.get("title", "")),
        content=str(data.get("content", "")),
        source_url=str(data.get("source_url", "")),
        source_type=str(data.get("source_type", "knowledge_chunk")),
        domain=str(data.get("domain", "general")),
        confidence_level=str(data.get("confidence_level", "medium")),
        data_period=str(data.get("data_period", "")),
        project_slug=data.get("project_slug"),
        zone_slug=data.get("zone_slug"),
        subzone_slug=data.get("subzone_slug"),
        building_code=data.get("building_code"),
        vector_score=float(data.get("vector_score") or 0.0),
        lexical_score=float(data.get("lexical_score") or 0.0),
        debug={"source": source},
    )
    return chunk


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{float(value):.8f}" for value in vector) + "]"


def get_retriever() -> Retriever:
    provider = get_settings().rag_provider
    if provider == "pgvector":
        return PgVectorHybridRetriever()
    return LegacyJsonRetriever()
