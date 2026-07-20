"""E2E Tests V2 — luồng khách hàng hoàn chỉnh theo BAN_THIET_KE_V2.

Journey chính (Mục 5 + Mục 15):
  1. Khách xem phân khu → chat ẩn danh → bị chặn sau 3 tin → điền form capture
     → chat tiếp → lead nóng → tự phân công sale → admin thấy trong CRM.
  2. Đa lượt chat cùng session: điểm cộng dồn, hồ sơ khách cập nhật dần.
"""

import uuid
from unittest.mock import patch

import pytest

from src.config import get_settings

MOCK_RESULT = {
    "response": "Mocked AI Response",
    "intent": "consult",
    "trigger_handover": False,
    "recommended_zones": [],
    "citations": [],
}


def _phone() -> str:
    return f"09{str(uuid.uuid4().int)[:8]}"


async def _admin_headers(client) -> dict:
    settings = get_settings()
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class TestFullJourneyBrowseChatCaptureCRM:
    """Browse → chat → gate → capture → chat tiếp → hot → CRM."""

    @pytest.mark.asyncio
    async def test_full_journey(self, client, monkeypatch):
        # Journey gửi 6 tin liên tiếp — tắt rate-limit để không nhiễu vào gating
        monkeypatch.setattr("src.api.agent_routes._rate_limited", lambda session_id: False)
        # ── 1. Khách xem danh sách + chi tiết phân khu ────────────────────
        listing = await client.get("/api/v1/subdivisions")
        assert listing.status_code == 200
        subdivisions = listing.json()
        assert len(subdivisions) > 0
        slug = subdivisions[0]["slug"]
        detail = await client.get(f"/api/v1/subdivisions/{slug}")
        assert detail.status_code == 200

        # ── 2. Chat ẩn danh 3 tin (miễn phí) ─────────────────────────────
        session_id = str(uuid.uuid4())
        with patch("src.api.agent_routes.agent.ainvoke") as mock_agent:
            mock_agent.return_value = MOCK_RESULT
            for i in range(3):
                response = await client.post(
                    "/agent/chat",
                    json={
                        "messages": [{"role": "user", "content": f"Câu hỏi {i} về {slug}"}],
                        "session_id": session_id,
                    },
                )
                assert response.status_code == 200
                assert response.json()["require_lead_capture"] is False

            # ── 3. Tin thứ 4 bị chặn → yêu cầu capture ───────────────────
            response = await client.post(
                "/agent/chat",
                json={
                    "messages": [{"role": "user", "content": "Câu hỏi thứ 4"}],
                    "session_id": session_id,
                },
            )
            assert response.json()["require_lead_capture"] is True

            # ── 4. Khách điền form Tạo đơn tư vấn ────────────────────────
            phone = _phone()
            capture = await client.post(
                "/api/v1/customers/capture",
                json={
                    "full_name": "Nguyễn E2E",
                    "phone": phone,
                    "session_id": session_id,
                    "interested_subdivision_slug": slug,
                    "preferred_unit_type": "2PN",
                    "budget_min": 3_000_000_000,
                    "budget_max": 4_000_000_000,
                    "purpose": "to_live",
                },
            )
            assert capture.status_code == 201
            customer_id = capture.json()["customer_id"]

            # ── 5. Chat tiếp bình thường sau capture ─────────────────────
            response = await client.post(
                "/agent/chat",
                json={
                    "messages": [{"role": "user", "content": "Tiếp tục tư vấn giúp tôi"}],
                    "session_id": session_id,
                },
            )
            assert response.json()["require_lead_capture"] is False

            # ── 6. Agent phát hiện lead nóng → handover ──────────────────
            mock_agent.return_value = {
                **MOCK_RESULT,
                "detected": {
                    "customer_type": "real_need",
                    "temperature": "hot",
                    "lead_score": 75,
                    "interested_subdivision": slug,
                    "budget_range": [3_000_000_000, 4_000_000_000],
                    "unit_type": "2PN",
                },
            }
            response = await client.post(
                "/agent/chat",
                json={
                    "messages": [{"role": "user", "content": "Tôi muốn đi xem nhà tuần này"}],
                    "session_id": session_id,
                },
            )
            assert response.json()["trigger_handover"] is True

        # ── 7. Admin thấy khách trong CRM với đầy đủ hồ sơ ────────────────
        headers = await _admin_headers(client)
        crm = await client.get(f"/api/v1/customers/{customer_id}", headers=headers)
        assert crm.status_code == 200
        customer = crm.json()
        assert customer["phone"] == phone
        assert customer["temperature"] == "hot"
        assert customer["lead_score"] == 75
        assert customer["customer_type"] == "real_need"
        assert customer["interested_subdivision"]["slug"] == slug
        assert customer["preferred_unit_type"] == "2PN"
        assert customer["status"] == "contacted"

        # ── 8. Admin xem lại đoạn chat của khách ──────────────────────────
        conversations = await client.get(
            f"/api/v1/customers/{customer_id}/conversations", headers=headers
        )
        assert conversations.status_code == 200
        convo_list = conversations.json()
        assert len(convo_list) == 1
        assert convo_list[0]["is_lead_captured"] is True
        assert convo_list[0]["user_message_count"] >= 5


class TestMultiTurnScoring:
    """Điểm lead cộng dồn qua nhiều lượt chat cùng session (pipeline thật)."""

    @pytest.mark.asyncio
    async def test_score_accumulates_across_turns(self, client, monkeypatch):
        class _FailingLLM:
            async def ainvoke(self, messages):
                raise ConnectionError("provider down (test)")

        monkeypatch.setattr(
            "src.agents.nodes.llm_node.get_llm", lambda temperature=None: _FailingLLM()
        )
        # Tắt mock mặc định của conftest để chạy pipeline thật
        import src.api.agent_routes as agent_routes
        from src.agents.graph import build_graph

        monkeypatch.setattr(agent_routes, "agent", build_graph())

        session_id = str(uuid.uuid4())

        first = await client.post(
            "/agent/chat",
            json={
                "messages": [{"role": "user", "content": "Ngân sách 3 tỷ mua The Zenpark"}],
                "session_id": session_id,
            },
        )
        first_score = first.json()["detected"]["lead_score"]
        assert first_score >= 10  # bàn ngân sách cụ thể

        second = await client.post(
            "/agent/chat",
            json={
                "messages": [{"role": "user", "content": "The Zenpark cho tôi đặt lịch xem nhà"}],
                "session_id": session_id,
            },
        )
        second_score = second.json()["detected"]["lead_score"]
        # visit +30 và zone focus +15 cộng dồn lên điểm cũ
        assert second_score >= first_score + 30
