import pytest

from src.agents.nodes.rag_node import rag_node
from src.services.knowledge_retriever import detect_subdivision_slugs, detect_topics, retrieve_knowledge_chunks
from src.services.recommender import get_zone_recommendations
from src.services.vinhomes_data import format_zones_for_context, get_all_zones, get_zone_by_slug


def _norm_dash(text: str) -> str:
    """Cleaned data may use hyphen or en-dash between price bounds."""
    return text.replace("–", "-")


def test_cleaned_data_adapter_exposes_zenpark_2pn_price():
    zone = get_zone_by_slug("the-zenpark")

    assert zone is not None
    assert "2PN" in zone["unit_types"]
    assert _norm_dash(zone["apartment_specs"]["2PN"]["price"]) == "3,0 - 3,5 tỷ"
    assert zone["apartment_specs"]["2PN"]["price_range_billion"] == {"min": 3.0, "max": 3.5}

    context = format_zones_for_context([zone])
    assert "The Zenpark" in context
    assert "2PN" in context
    assert "3,0 - 3,5 tỷ" in _norm_dash(context)
    assert "?-?" not in context


def test_cleaned_data_adapter_preserves_missing_price_state():
    zone = get_zone_by_slug("the-senique-hanoi")

    assert zone is not None
    assert zone["apartment_specs"]["2PN"]["price"] == "Đang cập nhật / Liên hệ CĐT"
    assert zone["apartment_specs"]["2PN"]["price_range_billion"] == {}

    context = format_zones_for_context([zone])
    assert "The Senique Hanoi" in context
    assert "2PN" in context
    assert "Đang cập nhật / Liên hệ CĐT" in context


def test_knowledge_retriever_detects_slug_and_topic():
    query = "The Zenpark căn 2PN giá bao nhiêu?"

    assert "the-zenpark" in detect_subdivision_slugs(query)
    assert "apartment_specs" in detect_topics(query)

    chunks = retrieve_knowledge_chunks(query, max_chunks=3)
    assert chunks
    assert chunks[0]["subdivision_slug"] == "the-zenpark"
    assert chunks[0]["topic"] == "apartment_specs"
    assert "3,0 - 3,5 tỷ" in _norm_dash(chunks[0]["content"])


@pytest.mark.asyncio
async def test_rag_context_uses_specific_chunks_for_zenpark_price():
    result = await rag_node({
        "intent": "price_query",
        "user_profile": {"unit_type": "2PN"},
        "messages": [{"role": "user", "content": "The Zenpark căn 2PN giá bao nhiêu?"}],
    })

    context = result["zone_context"]
    assert "source: the-zenpark/apartment_specs" in context
    assert "3,0 - 3,5 tỷ" in _norm_dash(context)
    assert result["recommended_zones"][0]["slug"] == "the-zenpark"
    assert _norm_dash(result["recommended_zones"][0]["price_range"]) == "3 - 3,5 tỷ"


def test_recommendation_uses_cleaned_price_ranges():
    recommendations = get_zone_recommendations(budget=3_000_000_000, unit_type="2PN", purpose="ở thật", top_k=5)

    assert recommendations
    assert any(item["slug"] == "the-zenpark" for item in recommendations)
    assert all(item["price_range"] != "Chưa cập nhật" for item in recommendations[:3])
    assert len(get_all_zones()) == 12
