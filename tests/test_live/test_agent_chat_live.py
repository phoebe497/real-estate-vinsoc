import os
import uuid

import pytest

from src.agents.graph import agent


@pytest.mark.live_llm
@pytest.mark.asyncio
async def test_live_agent_chat_uses_real_llm_and_rag():
    """Smoke test for the real provider, gated by RUN_LIVE_LLM_TESTS=1."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for live LLM tests")

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "The Zenpark có tiện ích nội khu gì nổi bật?",
                }
            ],
            "session_id": str(uuid.uuid4()),
        }
    )

    response = result.get("response", "")
    assert response
    assert result.get("intent") in {"consult", "zone_match", "price_query"}
    assert "Vinhomes" in response or "Zenpark" in response or "tiện ích" in response.lower()
