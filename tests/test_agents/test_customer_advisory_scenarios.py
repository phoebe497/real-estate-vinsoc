import pytest

from src.agents.nodes.intent_node import intent_node
from src.agents.nodes.llm_node import llm_node
from src.agents.nodes.rag_node import rag_node
from src.config import get_settings
from src.services.vinhomes_data import get_valid_zone_slugs

FAMILY_4_BUDGET_QUERY = (
    "Gia \u0111\u00ecnh t\u00f4i 4 ng\u01b0\u1eddi, "
    "c\u00f3 2 con nh\u1ecf h\u1ecdc c\u1ea5p 2. "
    "T\u00e0i ch\u00ednh t\u1ed1i \u0111a t\u1ea7m 4 t\u1ef7 "
    "v\u1eady th\u00ec l\u1ef1a ch\u1ecdn n\u00e0o s\u1ebd ph\u00f9 h\u1ee3p?"
)


@pytest.mark.asyncio
async def test_family_4_budget_4b_extracts_need_and_recommends_clear_zones(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "rag_provider", "legacy")

    intent = await intent_node({"messages": [{"role": "user", "content": FAMILY_4_BUDGET_QUERY}]})

    assert intent["trigger_handover"] is False
    assert intent["user_profile"]["budget"] == 4_000_000_000
    assert intent["user_profile"]["family_size"] == 4
    assert intent["user_profile"]["school_need"] is True

    rag_result = await rag_node({"messages": [{"role": "user", "content": FAMILY_4_BUDGET_QUERY}], **intent})

    assert rag_result["status"] == "ok"
    assert rag_result["recommended_zones"]
    valid_slugs = get_valid_zone_slugs()
    for zone in rag_result["recommended_zones"]:
        assert zone["slug"] in valid_slugs
        assert zone["price_range"]

    # LLM ph\u1ea3i \u0111\u01b0\u1ee3c g\u1ecdi TH\u1eacT v\u1edbi context RAG + profile kh\u00e1ch trong system prompt
    captured_prompts: list[str] = []

    class _FakeLLM:
        async def ainvoke(self, messages):
            captured_prompts.append(messages[0].content)

            class _Result:
                content = "V\u1edbi gia \u0111\u00ecnh 4 ng\u01b0\u1eddi v\u00e0 ng\u00e2n s\u00e1ch 4 t\u1ef7, em g\u1ee3i \u00fd c\u00e1c ph\u00e2n khu ph\u00f9 h\u1ee3p trong d\u1eef li\u1ec7u."

            return _Result()

    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: _FakeLLM())

    final = await llm_node(
        {
            "messages": [{"role": "user", "content": FAMILY_4_BUDGET_QUERY}],
            **intent,
            **rag_result,
        }
    )

    response = final["response"]
    assert final["status"] == "ok"
    assert "Th\u00f4ng tin n\u00e0y hi\u1ec7n ch\u01b0a" not in response
    assert "The Venice" not in response
    assert "The Milan" not in response
    assert "The Manhattan" not in response

    # System prompt ph\u1ea3i ch\u1ee9a profile kh\u00e1ch v\u00e0 context ph\u00e2n khu t\u1eeb RAG
    assert len(captured_prompts) == 1
    system_prompt = captured_prompts[0]
    assert "4 ng\u01b0\u1eddi" in system_prompt          # profile: family_size
    assert "4 t\u1ef7" in system_prompt             # profile: budget
    assert rag_result["recommended_zones"][0]["name"] in system_prompt  # RAG context th\u1eadt
