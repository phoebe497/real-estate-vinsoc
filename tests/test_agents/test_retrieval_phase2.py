from __future__ import annotations

import pytest

from src.agents.nodes.llm_node import _polish_response_format, llm_node
from src.config import get_settings
from src.services import embeddings
from src.services.citation_verifier import verify_and_render_citations
from src.services.embeddings import get_embeddings_client, local_hash_embedding
from src.services.retrieval import (
    LegacyJsonRetriever,
    PgVectorHybridRetriever,
    RetrievalQuery,
    RetrievedChunk,
    apply_metadata_filter,
    build_retrieval_query,
    get_retriever,
    normalize_query,
    pack_context,
    reciprocal_rank_fusion,
    remove_duplicate_chunks,
)


def _chunk(
    chunk_id: str,
    *,
    content: str = "The Zenpark has Japanese garden amenities.",
    domain: str = "amenities",
    zone_slug: str = "the-zenpark-vinhomes",
    source_url: str = "/phan-khu/the-zenpark-vinhomes",
    data_period: str = "2026-06",
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        title=f"Chunk {chunk_id}",
        content=content,
        source_url=source_url,
        source_type="knowledge_chunk",
        domain=domain,
        confidence_level="medium",
        data_period=data_period,
        zone_slug=zone_slug,
        relevance_score=0.5,
    )


def test_retriever_feature_flag(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_provider", "legacy")
    assert isinstance(get_retriever(), LegacyJsonRetriever)

    monkeypatch.setattr(settings, "rag_provider", "pgvector")
    assert isinstance(get_retriever(), PgVectorHybridRetriever)


def test_normalize_query_preserves_vietnamese_d_letters():
    assert normalize_query("Chủ đề đặt cọc đã bàn giao") == "chu de dat coc da ban giao"


def test_local_hash_embedding_is_deterministic():
    first = local_hash_embedding("The Zenpark tien ich vuon Nhat")
    second = local_hash_embedding("The Zenpark tien ich vuon Nhat")

    assert len(first) == get_settings().openai_embedding_dimensions
    assert first == second
    assert any(value != 0 for value in first)


def test_embedding_client_uses_embedding_specific_config(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_embedding_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "chat-key")
    monkeypatch.setattr(settings, "openai_base_url", "https://chat.example/v1")
    monkeypatch.setattr(settings, "openai_embedding_api_key", "embedding-key")
    monkeypatch.setattr(settings, "openai_embedding_base_url", "https://openrouter.ai/api/v1")
    monkeypatch.setattr(settings, "openai_embedding_model", "text-embedding-3-small")

    captured = {}

    class FakeEmbeddings:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(embeddings, "OpenAIEmbeddings", FakeEmbeddings)

    get_embeddings_client()

    assert captured["api_key"] == "embedding-key"
    assert captured["base_url"] == "https://openrouter.ai/api/v1"
    assert captured["model"] == "text-embedding-3-small"


def test_embedding_client_uses_openrouter_config(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_embedding_provider", "openrouter")
    monkeypatch.setattr(settings, "openai_api_key", "chat-key")
    monkeypatch.setattr(settings, "openai_base_url", "https://chat.example/v1")
    monkeypatch.setattr(settings, "openrouter_api_key", "openrouter-key")
    monkeypatch.setattr(settings, "openrouter_base_url", "https://openrouter.ai/api/v1")
    monkeypatch.setattr(settings, "openrouter_model", "openai/text-embedding-3-small")

    captured = {}

    class FakeEmbeddings:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(embeddings, "OpenAIEmbeddings", FakeEmbeddings)

    get_embeddings_client()

    assert captured["api_key"] == "openrouter-key"
    assert captured["base_url"] == "https://openrouter.ai/api/v1"
    assert captured["model"] == "openai/text-embedding-3-small"


def test_vector_lexical_fusion_is_deterministic():
    query = build_retrieval_query("Zenpark tien ich", domain="amenities")
    vector = [_chunk("a"), _chunk("b")]
    lexical = [_chunk("b"), _chunk("c")]

    fused = reciprocal_rank_fusion(vector, lexical, query)

    assert [chunk.chunk_id for chunk in fused][:2] == ["b", "a"]
    assert fused[0].relevance_score >= fused[1].relevance_score


def test_metadata_filter_keeps_matching_zone():
    query = RetrievalQuery(raw_query="x", normalized_query="x", zone_slugs=("the-zenpark-vinhomes",))
    chunks = [
        _chunk("match", zone_slug="the-zenpark-vinhomes"),
        _chunk("other", zone_slug="masteri-waterfront"),
    ]

    filtered = apply_metadata_filter(chunks, query)

    assert [chunk.chunk_id for chunk in filtered] == ["match"]


def test_domain_boost_increases_relevance():
    query = build_retrieval_query("gia can ho Zenpark", domain="price")
    price = _chunk("price", domain="price")
    amenity = _chunk("amenity", domain="amenities")

    fused = reciprocal_rank_fusion([amenity], [price], query)
    by_id = {chunk.chunk_id: chunk for chunk in fused}

    assert by_id["price"].metadata_score > by_id["amenity"].metadata_score


def test_duplicate_removal_uses_content_signature():
    duplicate = _chunk("duplicate", content="Same same same amenities content")
    original = _chunk("original", content="Same same same amenities content")

    deduped = remove_duplicate_chunks([original, duplicate])

    assert [chunk.chunk_id for chunk in deduped] == ["original"]


def test_context_token_budget_limits_selected_chunks():
    chunks = [
        _chunk("short", content="short context"),
        _chunk("long", content=" ".join(["long"] * 500)),
    ]

    context, selected, token_count = pack_context(chunks, token_budget=30)

    assert "[C1]" in context
    assert [chunk.citation_token for chunk in selected] == ["C1"]
    assert token_count <= 30


def test_citation_token_mapping_renders_trusted_links():
    chunk = _chunk("zen")
    chunk.citation_token = "C1"

    result = verify_and_render_citations("Zenpark co vuon Nhat [C1]", [chunk])

    assert result.response_text.endswith("[1](/phan-khu/the-zenpark-vinhomes)")
    assert result.citations[0]["citation_id"] == "1"
    assert result.citations[0]["chunk_id"] == "zen"


def test_fabricated_citation_link_is_removed():
    chunk = _chunk("zen")
    chunk.citation_token = "C1"

    result = verify_and_render_citations(
        "Thong tin [fake](/phan-khu/not-real-slug) va [C1]",
        [chunk],
    )

    assert "not-real-slug" not in result.response_text
    assert result.fabricated_links == ["not-real-slug"]


def test_invalid_slug_citation_is_rejected():
    chunk = _chunk("bad", source_url="/phan-khu/not-real-slug")
    chunk.citation_token = "C1"

    result = verify_and_render_citations("Thong tin [C1]", [chunk])

    assert not result.citations
    assert result.rejected_tokens == ["C1"]


def test_unused_citation_is_removed_from_response_citations():
    used = _chunk("used")
    unused = _chunk("unused")
    used.citation_token = "C1"
    unused.citation_token = "C2"

    result = verify_and_render_citations("Thong tin [C1]", [used, unused])

    assert [citation["chunk_id"] for citation in result.citations] == ["used"]
    assert result.unused_tokens == ["C2"]


def test_stale_price_warning_is_added():
    chunk = _chunk("old-price", domain="price", data_period="2025-01")
    chunk.citation_token = "C1"

    result = verify_and_render_citations("Gia tham khao 3 ty [C1]", [chunk])

    assert "stale_data_warning" in result.warnings
    assert result.response_text.startswith("[LƯU Ý]")


def test_expired_policy_rejection():
    chunk = _chunk("expired", domain="payment_policy", data_period="expired")
    chunk.citation_token = "C1"

    result = verify_and_render_citations("Chinh sach dang ap dung [C1]", [chunk])

    assert result.rejected_tokens == ["C1"]
    assert not result.citations


def test_response_format_polish_removes_markdown_heading_and_raw_status():
    response = "### 1) The Pavilion\n- Trạng thái: handed_over\n### 2) Masteri\n- Trạng thái: under_construction"

    polished = _polish_response_format(response)

    assert "###" not in polished
    assert "handed_over" not in polished
    assert "under_construction" not in polished
    assert "Trạng thái:" not in polished
    assert "ưu tiên dọn vào ở sớm" in polished
    assert "có thể chờ thêm" in polished


@pytest.mark.asyncio
async def test_no_context_refusal_does_not_call_generation(monkeypatch):
    called = False

    def fake_get_llm(temperature=None):
        nonlocal called
        called = True
        return None

    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", fake_get_llm)

    result = await llm_node(
        {
            "messages": [{"role": "user", "content": "Gia can ho bao nhieu?"}],
            "intent": "price_query",
            "zone_context": "",
            "status": "insufficient_context",
            "retrieved_chunks": [],
            "retrieval_debug": {},
        }
    )

    assert called is False
    assert result["status"] == "insufficient_context"


@pytest.mark.asyncio
async def test_llm_gateway_error_prefers_zone_context_fallback(monkeypatch):
    """When the LLM fails but RAG already picked zones, answer from zone context."""
    chunk = _chunk("amenity", content="- Hồ Ngọc Trai 24.5ha.\n- Biển hồ Crystal Lagoons 6.1ha.")
    chunk.citation_token = "C1"

    class FailingLLM:
        async def ainvoke(self, messages):
            raise ConnectionError("provider down")

    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: FailingLLM())

    result = await llm_node(
        {
            "messages": [{"role": "user", "content": "Ocean Park có tiện ích gì?"}],
            "intent": "consult",
            "zone_context": "[C1] Amenity context",
            "status": "ok",
            "retrieved_chunks": [chunk],
            "recommended_zones": [
                {
                    "name": "The Zenpark Vinhomes",
                    "slug": "the-zenpark-vinhomes",
                    "match_reason": "Có tiện ích phù hợp",
                    "price_range": "",
                    "design_style": "Japanese",
                }
            ],
            "retrieval_debug": {
                "domain": "amenities",
                "retrieval_latency_ms": 12,
                "total_latency_ms": 12,
                "retrieved_count": 1,
                "selected_chunk_count": 1,
                "context_token_count": 20,
            },
        }
    )

    assert result["status"] == "ok"
    assert "sự cố kỹ thuật" not in result["response"]
    assert "The Zenpark Vinhomes" in result["response"]
    assert result["citation_debug"]["status"] == "fallback_from_zone_context"


@pytest.mark.asyncio
async def test_llm_gateway_error_uses_retrieved_context_fallback(monkeypatch):
    """Without recommended zones, fall back to trusted retrieved chunks with citations."""
    chunk = _chunk("amenity", content="- Hồ Ngọc Trai 24.5ha.\n- Biển hồ Crystal Lagoons 6.1ha.")
    chunk.citation_token = "C1"

    class FailingLLM:
        async def ainvoke(self, messages):
            raise ConnectionError("provider down")

    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: FailingLLM())

    result = await llm_node(
        {
            "messages": [{"role": "user", "content": "Ocean Park có tiện ích gì?"}],
            "intent": "consult",
            "zone_context": "",
            "status": "ok",
            "retrieved_chunks": [chunk],
            "recommended_zones": [],
            "retrieval_debug": {
                "domain": "amenities",
                "retrieval_latency_ms": 12,
                "total_latency_ms": 12,
                "retrieved_count": 1,
                "selected_chunk_count": 1,
                "context_token_count": 20,
            },
        }
    )

    assert result["status"] == "ok"
    assert "sự cố kỹ thuật" not in result["response"]
    assert "Hồ Ngọc Trai" in result["response"]
    assert result["citations"][0]["chunk_id"] == "amenity"
    assert result["citation_debug"]["fallback_reason"] == "llm_gateway_error"
