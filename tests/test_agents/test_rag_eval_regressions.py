from __future__ import annotations

import pytest

from src.agents.nodes.intent_node import intent_node
from src.agents.nodes.llm_node import _polish_response_format
from src.agents.nodes.rag_node import rag_node
from src.config import get_settings
from src.services.retrieval import PgVectorHybridRetriever, build_retrieval_query

BUDGET_FAMILY_QUERY = (
    "Chào bạn, tôi đang có khoảng 3.5 tỷ, muốn tìm căn 2 phòng ngủ để gia đình "
    "dọn vào ở. Tôi thích phong cách hiện đại và có tiện ích cho trẻ em."
)

AMENITIES_QUERY = (
    "Ngoài việc mua nhà ra thì ở Ocean Park Gia Lâm có những tiện ích gì nổi bật "
    "không? Tôi nghe nói có hồ nhân tạo?"
)


@pytest.mark.asyncio
async def test_budget_2pn_family_consult_does_not_trigger_handover():
    result = await intent_node({"messages": [{"role": "user", "content": BUDGET_FAMILY_QUERY}]})

    assert result["intent"] in {"consult", "zone_match", "price_query"}
    assert result["trigger_handover"] is False
    assert result["user_profile"]["budget"] == 3_500_000_000
    assert result["user_profile"]["unit_type"] == "2PN"


@pytest.mark.asyncio
async def test_pgvector_empty_results_fall_back_to_vectorless_amenity_retrieval(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_provider", "pgvector")

    async def empty_candidates(self, query):
        return [], []

    async def no_embedding(query):
        return None

    monkeypatch.setattr(PgVectorHybridRetriever, "_retrieve_candidates", empty_candidates)
    monkeypatch.setattr("src.agents.nodes.rag_node.try_embed_query", no_embedding)

    result = await rag_node(
        {
            "messages": [{"role": "user", "content": AMENITIES_QUERY}],
            "intent": "consult",
            "user_profile": {},
        }
    )

    assert result["status"] == "ok"
    assert result["retrieved_chunks"]
    assert any(chunk.domain == "amenities" for chunk in result["retrieved_chunks"])
    assert "Hồ Ngọc Trai" in result["zone_context"]
    assert "Crystal" in result["zone_context"]


def test_gia_lam_amenity_query_is_not_misclassified_as_price():
    query = build_retrieval_query(
        "Ngoài việc mua nhà ra thì ở Ocean Park Gia Lâm có những tiện ích gì nổi bật không?"
    )

    assert query.domain == "amenities"


@pytest.mark.asyncio
async def test_school_family_query_returns_context_and_recommended_zones(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_provider", "pgvector")

    async def no_embedding(query):
        return None

    monkeypatch.setattr("src.agents.nodes.rag_node.try_embed_query", no_embedding)

    school_query = "Tôi muốn tư vấn phân khu gần trường học nhà tôi có 2 con nhỏ học trung học"
    intent = await intent_node({"messages": [{"role": "user", "content": school_query}]})
    result = await rag_node({"messages": [{"role": "user", "content": school_query}], **intent})

    assert intent["trigger_handover"] is False
    assert result["status"] == "ok"
    assert result["retrieved_chunks"]
    assert result["recommended_zones"]
    context = result["zone_context"].lower()
    assert any(term in context for term in ("trường", "vinschool", "vinuni", "brighton"))


@pytest.mark.asyncio
async def test_core_advisory_queries_do_not_return_insufficient_context(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_provider", "pgvector")

    async def no_embedding(query):
        return None

    monkeypatch.setattr("src.agents.nodes.rag_node.try_embed_query", no_embedding)

    queries = [
        "Tôi muốn tư vấn phân khu gần trường học nhà tôi có 2 con nhỏ học trung học",
        "Ngoài việc mua nhà ra thì ở Ocean Park Gia Lâm có những tiện ích gì nổi bật không? Tôi nghe nói có hồ nhân tạo?",
        "Tôi muốn căn gần Vincom và trường học",
        "The Zenpark có tiện ích gì nổi bật?",
    ]
    for query in queries:
        intent = await intent_node({"messages": [{"role": "user", "content": query}]})
        result = await rag_node({"messages": [{"role": "user", "content": query}], **intent})

        assert result["status"] == "ok", query
        assert result["retrieved_chunks"], query


@pytest.mark.asyncio
async def test_explicit_zone_query_keeps_matching_zone_card(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_provider", "pgvector")

    async def no_embedding(query):
        return None

    monkeypatch.setattr("src.agents.nodes.rag_node.try_embed_query", no_embedding)

    query = "The Pavilion có căn 2PN khoảng giá thế nào?"
    intent = await intent_node({"messages": [{"role": "user", "content": query}]})
    result = await rag_node({"messages": [{"role": "user", "content": query}], **intent})

    assert result["status"] == "ok"
    assert result["recommended_zones"]
    assert result["recommended_zones"][0]["slug"] == "the-pavilion-vinhomes"
    assert getattr(result["retrieved_chunks"][0], "zone_slug") == "the-pavilion-vinhomes"


def test_response_polish_hides_raw_status_labels():
    raw = "### 1) The Pavilion\n- Trạng thái: handed_over\n### 2) Masteri\n- Trạng thái: under_construction"

    polished = _polish_response_format(raw)

    assert "###" not in polished
    assert "Trạng thái:" not in polished
    assert "handed_over" not in polished
    assert "under_construction" not in polished
    assert "ưu tiên dọn vào ở sớm" in polished
    assert "có thể chờ thêm" in polished
