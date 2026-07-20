"""Pipeline agent thật (intent → rag → profile → llm) trả detected + score."""

import pytest

from src.agents.graph import agent


class _FailingLLM:
    async def ainvoke(self, messages):
        raise ConnectionError("provider down (test)")


@pytest.mark.asyncio
async def test_pipeline_returns_detected_profile(monkeypatch):
    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: _FailingLLM())

    result = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "Ngân sách 3 tỷ, tôi muốn đặt lịch xem nhà The Zenpark"}
            ],
            "profile_messages": [
                {"role": "user", "content": "Ngân sách 3 tỷ, tôi muốn đặt lịch xem nhà The Zenpark"}
            ],
            "session_id": "test-pipeline",
            "current_lead_score": 0,
        }
    )

    detected = result["detected"]
    # visit +30, budget +10 → 40 (warm)
    assert detected["lead_score"] >= 40
    assert detected["temperature"] in ("warm", "hot")
    assert detected["interested_subdivision"] == "the-zenpark"
    assert detected["score_delta"] == detected["lead_score"]
    assert result.get("response")  # fallback vẫn có câu trả lời dù LLM lỗi


@pytest.mark.asyncio
async def test_pipeline_handover_intent_still_scored(monkeypatch):
    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: _FailingLLM())

    result = await agent.ainvoke(
        {
            "messages": [{"role": "user", "content": "Tôi muốn đặt cọc, cho gặp sale"}],
            "profile_messages": [{"role": "user", "content": "Tôi muốn đặt cọc, cho gặp sale"}],
            "session_id": "test-handover",
            "current_lead_score": 10,
        }
    )

    assert result["trigger_handover"] is True
    detected = result["detected"]
    # 10 + 25 (deposit) + 25 (meet sale) = 60 → hot
    assert detected["lead_score"] == 60
    assert detected["temperature"] == "hot"
