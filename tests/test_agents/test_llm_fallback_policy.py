import pytest

from src.agents.nodes.llm_node import llm_node
from src.services.citation_verifier import CitationVerifierResult


@pytest.mark.asyncio
async def test_llm_failure_uses_zone_context_instead_of_generic_insufficient_context(monkeypatch):
    class FailingLLM:
        async def ainvoke(self, messages):
            raise RuntimeError("provider unavailable")

    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: FailingLLM())

    result = await llm_node(
        {
            "messages": [{"role": "user", "content": "Toi can 2PN thi phan khu nao hop ly?"}],
            "intent": "consult",
            "status": "insufficient_context",
            "zone_context": (
                "The Zenpark phu hop voi khach can khong gian yen tinh, "
                "thiet ke canh quan Nhat va can can 2PN cho gia dinh."
            ),
            "recommended_zones": [
                {
                    "name": "The Zenpark",
                    "slug": "the-zenpark-vinhomes",
                    "match_reason": "phu hop nhu cau 2PN va khong gian song yen tinh",
                    "price_range": "tham khao theo du lieu du an",
                }
            ],
            "retrieval_debug": {},
            "citations": [],
        }
    )

    assert result["status"] == "ok"
    assert "chua co du nguon" not in result["response"].lower()
    assert "The Zenpark" in result["response"]
    assert result["citation_debug"]["status"] == "fallback_from_zone_context"


@pytest.mark.asyncio
async def test_non_sensitive_advisory_answer_is_not_replaced_by_citation_fallback(monkeypatch):
    class FakeLLM:
        async def ainvoke(self, messages):
            class Response:
                content = (
                    "The Zenpark phu hop neu anh chi can khong gian yen tinh, "
                    "nhieu canh quan va cam giac rieng tu."
                )

            return Response()

    def fake_verifier(response_text, chunks):
        return CitationVerifierResult(
            response_text=response_text,
            citations=[],
            status="insufficient_context",
            warnings=["missing_optional_citation"],
        )

    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: FakeLLM())
    monkeypatch.setattr("src.agents.nodes.llm_node.verify_and_render_citations", fake_verifier)

    result = await llm_node(
        {
            "messages": [{"role": "user", "content": "Toi can 2PN khu Zenpark."}],
            "intent": "consult",
            "status": "ok",
            "zone_context": (
                "The Zenpark co canh quan phong cach Nhat, "
                "phu hop khach can khong gian yen tinh."
            ),
            "recommended_zones": [
                {
                    "name": "The Zenpark",
                    "slug": "the-zenpark-vinhomes",
                    "match_reason": "phu hop nhu cau 2PN",
                    "price_range": "",
                }
            ],
            "retrieval_debug": {},
            "retrieved_chunks": [],
        }
    )

    assert result["status"] == "ok"
    assert "chua co du nguon" not in result["response"].lower()
    assert "The Zenpark" in result["response"]


@pytest.mark.asyncio
async def test_llm_only_receives_latest_user_question(monkeypatch):
    seen_messages = []

    class FakeLLM:
        async def ainvoke(self, messages):
            seen_messages.extend(messages)

            class Response:
                content = "Ngoai Zenpark, anh chi co the tham khao The Pavilion hoac The Sapphire."

            return Response()

    monkeypatch.setattr("src.agents.nodes.llm_node.get_llm", lambda temperature=None: FakeLLM())

    result = await llm_node(
        {
            "messages": [
                {"role": "user", "content": "toi can 2PN"},
                {"role": "assistant", "content": "Anh chi can ngan sach bao nhieu?"},
                {"role": "user", "content": "con phan khu nao khac ngoai zenpark khong"},
            ],
            "intent": "consult",
            "status": "ok",
            "zone_context": (
                "The Zenpark, The Pavilion va The Sapphire deu la cac phan khu co the tu van "
                "theo nhu cau can ho 2PN."
            ),
            "recommended_zones": [],
            "retrieval_debug": {},
            "retrieved_chunks": [],
        }
    )

    human_messages = [message.content for message in seen_messages if message.type == "human"]
    assert human_messages == ["con phan khu nao khac ngoai zenpark khong"]
    assert result["status"] == "ok"
