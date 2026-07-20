"""Integration Tests — API endpoints + DB interactions (Medium size).

Tests cross-boundary interactions:
  - POST/GET/PATCH endpoints with real DB session
  - Admin auth guard
  - Rate limiting with real message persistence
  - Recommend endpoint with real zone data
  - Lead CRUD lifecycle
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from src.config import get_settings


async def _admin_headers(client) -> dict[str, str]:
    settings = get_settings()
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Health & Status Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class TestHealthEndpoints:

    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "env" in data

    @pytest.mark.asyncio
    async def test_agent_status_returns_endpoints(self, client):
        response = await client.get("/agent/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "chat" in data["endpoints"]
        assert "recommend" in data["endpoints"]
        assert "customer_score" in data["endpoints"]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Admin Authentication Guard
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdminAuth:
    """CRM V2 dùng JWT — không token thì 401."""

    @pytest.mark.asyncio
    async def test_customers_list_without_token_returns_401(self, client):
        response = await client.get("/api/v1/customers")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_customers_list_with_invalid_token_returns_401(self, client):
        response = await client.get(
            "/api/v1/customers", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_dashboard_requires_token(self, client):
        response = await client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_throttles_repeated_failures(self, client, monkeypatch):
        settings = get_settings()
        monkeypatch.setattr(settings, "login_ip_rate_limit_per_minute", 2)
        monkeypatch.setattr(settings, "login_account_rate_limit_per_minute", 2)
        payload = {"email": settings.admin_email, "password": "definitely-wrong"}

        for _ in range(2):
            response = await client.post("/api/v1/auth/login", json=payload)
            assert response.status_code == 401

        blocked = await client.post("/api/v1/auth/login", json=payload)
        assert blocked.status_code == 429
        assert blocked.headers["retry-after"] == "60"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. POST /agent/chat — Integration with DB
# ═══════════════════════════════════════════════════════════════════════════════


class TestChatEndpoint:

    @pytest.mark.asyncio
    async def test_chat_creates_conversation_and_returns_response(self, client):
        """Chat endpoint persists conversation in DB and returns AI response."""
        session_id = str(uuid.uuid4())
        payload = {
            "messages": [{"role": "user", "content": "Xin chào"}],
            "session_id": session_id,
        }
        response = await client.post("/agent/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["session_id"] == session_id
        assert isinstance(data["trigger_handover"], bool)

    @pytest.mark.asyncio
    async def test_chat_auto_generates_session_id(self, client):
        """If no session_id is provided, one is generated automatically."""
        payload = {
            "messages": [{"role": "user", "content": "Hello"}],
        }
        response = await client.post("/agent/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"]  # Not empty
        assert len(data["session_id"]) > 10  # Looks like a UUID

    @pytest.mark.asyncio
    async def test_chat_validates_empty_messages(self, client):
        """Empty messages list should fail validation."""
        response = await client.post("/agent/chat", json={"messages": []})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_validates_empty_content(self, client):
        """Message with empty content should fail validation."""
        response = await client.post("/agent/chat", json={
            "messages": [{"role": "user", "content": ""}],
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_rejects_non_uuid_session_id(self, client):
        response = await client.post(
            "/agent/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "session_id": "attacker-controlled-key",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_ip_limit_cannot_be_bypassed_by_rotating_session_ids(
        self, client, monkeypatch
    ):
        settings = get_settings()
        monkeypatch.setattr(settings, "chat_ip_rate_limit_per_minute", 3)

        for _ in range(3):
            response = await client.post(
                "/agent/chat",
                json={
                    "messages": [{"role": "user", "content": "Xin tư vấn"}],
                    "session_id": str(uuid.uuid4()),
                },
            )
            assert response.status_code == 200
            assert response.json()["analysis"] != "rate_limited"

        blocked = await client.post(
            "/agent/chat",
            json={
                "messages": [{"role": "user", "content": "Xin tư vấn tiếp"}],
                "session_id": str(uuid.uuid4()),
            },
        )
        assert blocked.status_code == 200
        assert blocked.json()["analysis"] == "rate_limited"

    @pytest.mark.asyncio
    async def test_chat_rate_limiter_triggers_at_6th_message(self, client):
        """After 5 messages in 1 minute, 6th message returns rate limit response (HTTP 200)."""
        session_id = str(uuid.uuid4())

        with patch("src.api.agent_routes.agent.ainvoke") as mock_ainvoke:
            mock_ainvoke.return_value = {
                "response": "Mocked AI Response",
                "intent": "consult",
                "trigger_handover": False,
                "recommended_zones": [],
            }

            for i in range(5):
                payload = {
                    "messages": [{"role": "user", "content": f"Câu hỏi {i}"}],
                    "session_id": session_id,
                }
                response = await client.post("/agent/chat", json=payload)
                assert response.status_code == 200

            # 6th request — rate limited
            payload = {
                "messages": [{"role": "user", "content": "Câu hỏi thứ 6"}],
                "session_id": session_id,
            }
            response = await client.post("/agent/chat", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["analysis"] == "rate_limited"
            assert "đợi" in data["response"].lower() or "nhiều" in data["response"].lower()


# ═══════════════════════════════════════════════════════════════════════════════
# 4. POST /agent/recommend — Integration with zone data
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecommendEndpoint:

    @pytest.mark.asyncio
    async def test_recommend_returns_zones(self, client):
        payload = {"budget": 3_000_000_000, "unit_type": "2PN", "purpose": "ở thật"}
        response = await client.post("/agent/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["recommendations"]) >= 1
        zone = data["recommendations"][0]
        assert "name" in zone
        assert "slug" in zone
        assert "match_reason" in zone
        assert "score" in zone

    @pytest.mark.asyncio
    async def test_recommend_respects_top_k(self, client):
        payload = {"budget": 3_000_000_000, "top_k": 1}
        response = await client.post("/agent/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) <= 1

    @pytest.mark.asyncio
    async def test_recommend_empty_filters_still_works(self, client):
        response = await client.post("/agent/recommend", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_recommend_validates_top_k_range(self, client):
        response = await client.post("/agent/recommend", json={"top_k": 100})
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# 5. POST /api/v1/leads — Lead Creation + AI Scoring
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# 6. POST /agent/lead-score — Standalone scoring
# ═══════════════════════════════════════════════════════════════════════════════


class TestLeadScoreEndpoint:

    @pytest.mark.asyncio
    async def test_lead_score_returns_valid_score(self, client):
        headers = await _admin_headers(client)
        payload = {
            "name": "Phạm Score Test",
            "phone": "0912345678",
            "chat_history": [],
            "user_profile": {
                "budget": 5_000_000_000,
                "purpose": "đầu tư",
            },
        }
        response = await client.post("/agent/customer-score", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["score"] in ("HOT", "WARM", "COLD")
        assert data["name"] == "Phạm Score Test"
        assert data["phone"] == "0912345678"

    @pytest.mark.asyncio
    async def test_lead_score_validates_phone(self, client):
        headers = await _admin_headers(client)
        payload = {
            "name": "Test",
            "phone": "not-a-phone",
        }
        response = await client.post("/agent/customer-score", json=payload, headers=headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_lead_score_requires_authentication(self, client):
        response = await client.post(
            "/agent/customer-score",
            json={"name": "Unauthorized", "phone": "0912345678"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_lead_score_is_rate_limited_per_user(self, client, monkeypatch):
        settings = get_settings()
        monkeypatch.setattr(settings, "customer_score_rate_limit_per_minute", 2)
        headers = await _admin_headers(client)
        payload = {"name": "Rate Limited", "phone": "0912345678"}

        with patch(
            "src.api.agent_routes.score_lead_detail",
            new_callable=AsyncMock,
            return_value={
                "score": "COLD",
                "numeric_score": 0,
                "score_reason": "test",
                "breakdown": {},
                "handover_recommended": False,
            },
        ):
            for _ in range(2):
                response = await client.post(
                    "/agent/customer-score",
                    json=payload,
                    headers=headers,
                )
                assert response.status_code == 200

            blocked = await client.post(
                "/agent/customer-score",
                json=payload,
                headers=headers,
            )

        assert blocked.status_code == 429
        assert blocked.headers["retry-after"] == "60"
