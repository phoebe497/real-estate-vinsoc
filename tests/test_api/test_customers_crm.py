"""Tests V2: lead capture, chat gating, CRM customers, RBAC, sales, dashboard.

Bám theo tiêu chí nghiệm thu BAN_THIET_KE_V2.md Mục 15.
"""

import uuid
from unittest.mock import patch

import pytest

MOCK_AGENT_RESULT = {
    "response": "Mocked AI Response",
    "intent": "consult",
    "trigger_handover": False,
    "recommended_zones": [],
    "citations": [],
}


def _phone() -> str:
    """SĐT VN hợp lệ, ngẫu nhiên để tránh trùng giữa các test."""
    digits = str(uuid.uuid4().int)[:8]
    return f"09{digits}"


async def _admin_token(client) -> str:
    from src.config import get_settings

    settings = get_settings()
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_sale(client, admin_headers, *, permissions: list[str] | None = None) -> tuple[int, str]:
    """Tạo sale mới, cấp quyền nếu có, trả về (sale_id, token)."""
    email = f"sale-{uuid.uuid4().hex[:8]}@x.vn"
    response = await client.post(
        "/api/v1/sales",
        json={"email": email, "full_name": "Sale Test", "password": "password123"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    sale_id = response.json()["id"]
    if permissions:
        response = await client.put(
            f"/api/v1/sales/{sale_id}/permissions", json={"codes": permissions}, headers=admin_headers
        )
        assert response.status_code == 200, response.text
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 200
    return sale_id, login.json()["access_token"]


# ── Lead capture + chat gating (Mục 5.1) ─────────────────────────────────────


class TestChatGating:
    @pytest.mark.asyncio
    async def test_block_after_free_limit_and_unlock_by_capture(self, client):
        session_id = str(uuid.uuid4())

        with patch("src.api.agent_routes.agent.ainvoke") as mock_agent:
            mock_agent.return_value = MOCK_AGENT_RESULT
            # 3 tin đầu (FREE_MESSAGE_LIMIT=3) trả lời bình thường
            for i in range(3):
                response = await client.post(
                    "/agent/chat",
                    json={
                        "messages": [{"role": "user", "content": f"Câu hỏi {i} về The Zenpark"}],
                        "session_id": session_id,
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert data["require_lead_capture"] is False, f"blocked too early at message {i}"

            # Tin thứ 4 → chặn, yêu cầu để lại thông tin, KHÔNG gọi LLM
            call_count_before = mock_agent.call_count
            response = await client.post(
                "/agent/chat",
                json={
                    "messages": [{"role": "user", "content": "Câu hỏi thứ 4"}],
                    "session_id": session_id,
                },
            )
            data = response.json()
            assert data["require_lead_capture"] is True
            assert mock_agent.call_count == call_count_before

            # Submit form capture → mở khóa
            phone = _phone()
            capture = await client.post(
                "/api/v1/customers/capture",
                json={"full_name": "Nguyễn Gating", "phone": phone, "session_id": session_id},
            )
            assert capture.status_code == 201

            response = await client.post(
                "/agent/chat",
                json={
                    "messages": [{"role": "user", "content": "Câu hỏi thứ 5 sau khi capture"}],
                    "session_id": session_id,
                },
            )
            data = response.json()
            assert data["require_lead_capture"] is False
            assert data["response"] == "Mocked AI Response"

    @pytest.mark.asyncio
    async def test_phone_in_chat_captures_customer(self, client):
        session_id = str(uuid.uuid4())
        phone = _phone()

        response = await client.post(
            "/agent/chat",
            json={
                "messages": [
                    {"role": "user", "content": f"Tôi là Trần Chat, số điện thoại {phone} nhé"}
                ],
                "session_id": session_id,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["trigger_handover"] is True
        assert data["analysis"] == "lead_captured"

        # Khách xuất hiện trong CRM
        token = await _admin_token(client)
        customers = await client.get(
            "/api/v1/customers", params={"search": phone}, headers=_auth(token)
        )
        assert customers.status_code == 200
        found = customers.json()
        assert len(found) == 1
        assert found[0]["phone"] == phone
        assert found[0]["source"] == "chat"


class TestCapture:
    @pytest.mark.asyncio
    async def test_capture_creates_customer_with_details(self, client):
        phone = _phone()
        response = await client.post(
            "/api/v1/customers/capture",
            json={
                "full_name": "Lê Capture",
                "phone": phone,
                "email": "le@x.vn",
                "preferred_unit_type": "2PN",
                "budget_min": 3_000_000_000,
                "budget_max": 4_000_000_000,
                "purpose": "to_live",
                "interested_subdivision_slug": "the-zenpark",
                "consent_contact": True,
            },
        )
        assert response.status_code == 201
        customer_id = response.json()["customer_id"]

        token = await _admin_token(client)
        detail = await client.get(f"/api/v1/customers/{customer_id}", headers=_auth(token))
        assert detail.status_code == 200
        data = detail.json()
        assert data["full_name"] == "Lê Capture"
        assert data["preferred_unit_type"] == "2PN"
        assert data["purpose"] == "to_live"
        assert data["interested_subdivision"]["slug"] == "the-zenpark"

    @pytest.mark.asyncio
    async def test_capture_dedupes_by_phone(self, client):
        phone = _phone()
        first = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách A", "phone": phone}
        )
        second = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách A Sửa", "phone": phone}
        )
        assert first.json()["customer_id"] == second.json()["customer_id"]

    @pytest.mark.asyncio
    async def test_capture_rejects_invalid_phone(self, client):
        response = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Sai Phone", "phone": "12345"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_public_contact_form(self, client):
        phone = _phone()
        response = await client.post(
            "/api/v1/contact",
            json={"name": "Liên Hệ", "phone": phone, "message": "Tư vấn 3PN"},
        )
        assert response.status_code == 201


# ── RBAC / visibility (Mục 10) ───────────────────────────────────────────────


class TestRBAC:
    @pytest.mark.asyncio
    async def test_sale_sees_only_assigned_customers(self, client):
        admin_token = await _admin_token(client)
        admin_headers = _auth(admin_token)

        capture = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách Của Sale", "phone": _phone()}
        )
        customer_id = capture.json()["customer_id"]
        other = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách Khác", "phone": _phone()}
        )
        other_id = other.json()["customer_id"]

        sale_id, sale_token = await _create_sale(client, admin_headers)
        assign = await client.post(
            f"/api/v1/customers/{customer_id}/assign",
            json={"sale_id": sale_id},
            headers=admin_headers,
        )
        assert assign.status_code == 200

        listing = await client.get("/api/v1/customers", headers=_auth(sale_token))
        ids = [c["id"] for c in listing.json()]
        assert customer_id in ids
        assert other_id not in ids

        detail = await client.get(f"/api/v1/customers/{other_id}", headers=_auth(sale_token))
        assert detail.status_code == 404

    @pytest.mark.asyncio
    async def test_sale_without_permission_cannot_edit_or_assign(self, client):
        admin_headers = _auth(await _admin_token(client))
        capture = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách Edit", "phone": _phone()}
        )
        customer_id = capture.json()["customer_id"]
        sale_id, sale_token = await _create_sale(client, admin_headers)
        await client.post(
            f"/api/v1/customers/{customer_id}/assign", json={"sale_id": sale_id}, headers=admin_headers
        )

        edit = await client.patch(
            f"/api/v1/customers/{customer_id}",
            json={"status": "contacted"},
            headers=_auth(sale_token),
        )
        assert edit.status_code == 403

        assign = await client.post(
            f"/api/v1/customers/{customer_id}/assign",
            json={"sale_id": None},
            headers=_auth(sale_token),
        )
        assert assign.status_code == 403

    @pytest.mark.asyncio
    async def test_granted_permission_unlocks_action(self, client):
        admin_headers = _auth(await _admin_token(client))
        capture = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách Perm", "phone": _phone()}
        )
        customer_id = capture.json()["customer_id"]
        sale_id, sale_token = await _create_sale(
            client, admin_headers, permissions=["customer.edit", "customer.view_all"]
        )

        edit = await client.patch(
            f"/api/v1/customers/{customer_id}",
            json={"status": "contacted", "temperature": "warm"},
            headers=_auth(sale_token),
        )
        assert edit.status_code == 200
        assert edit.json()["status"] == "contacted"

    @pytest.mark.asyncio
    async def test_me_returns_permissions_for_menu(self, client):
        admin_headers = _auth(await _admin_token(client))
        _, sale_token = await _create_sale(client, admin_headers, permissions=["dashboard.view"])

        me = await client.get("/api/v1/auth/me", headers=_auth(sale_token))
        assert me.status_code == 200
        data = me.json()
        assert data["user"]["role"] == "sale"
        assert data["permissions"] == ["dashboard.view"]

        admin_me = await client.get("/api/v1/auth/me", headers=admin_headers)
        assert "customer.view_all" in admin_me.json()["permissions"]


# ── CRM chi tiết: notes, purchases, conversations ────────────────────────────


class TestCustomerDetail:
    @pytest.mark.asyncio
    async def test_notes_and_purchases_flow(self, client):
        admin_headers = _auth(await _admin_token(client))
        capture = await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách Mua", "phone": _phone()}
        )
        customer_id = capture.json()["customer_id"]

        note = await client.post(
            f"/api/v1/customers/{customer_id}/notes",
            json={"content": "Khách hẹn xem nhà cuối tuần"},
            headers=admin_headers,
        )
        assert note.status_code == 201

        subdivisions = await client.get("/api/v1/subdivisions")
        subdivision_id_resp = await client.get(
            f"/api/v1/customers/{customer_id}", headers=admin_headers
        )
        assert subdivisions.status_code == 200
        # Lấy id phân khu đầu tiên qua sales endpoint (subdivisions public trả slug)
        first_slug = subdivisions.json()[0]["slug"]
        capture2 = await client.post(
            "/api/v1/customers/capture",
            json={
                "full_name": "Tmp",
                "phone": _phone(),
                "interested_subdivision_slug": first_slug,
            },
        )
        tmp_detail = await client.get(
            f"/api/v1/customers/{capture2.json()['customer_id']}", headers=admin_headers
        )
        subdivision_id = tmp_detail.json()["interested_subdivision"]["id"]

        purchase = await client.post(
            f"/api/v1/customers/{customer_id}/purchases",
            json={
                "subdivision_id": subdivision_id,
                "unit_type": "2PN",
                "purchase_date": "2026-07-01",
                "price": 3_500_000_000,
                "status": "deposit",
            },
            headers=admin_headers,
        )
        assert purchase.status_code == 201, purchase.text

        detail = await client.get(f"/api/v1/customers/{customer_id}", headers=admin_headers)
        data = detail.json()
        assert len(data["notes"]) == 1
        assert len(data["purchases"]) == 1
        assert data["status"] == "won"  # có giao dịch → won
        assert subdivision_id_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_views_customer_conversation(self, client):
        session_id = str(uuid.uuid4())
        phone = _phone()
        with patch("src.api.agent_routes.agent.ainvoke") as mock_agent:
            mock_agent.return_value = MOCK_AGENT_RESULT
            await client.post(
                "/agent/chat",
                json={
                    "messages": [{"role": "user", "content": "Câu hỏi trước capture"}],
                    "session_id": session_id,
                },
            )
        await client.post(
            "/api/v1/customers/capture",
            json={"full_name": "Khách Chat", "phone": phone, "session_id": session_id},
        )

        admin_headers = _auth(await _admin_token(client))
        customers = await client.get(
            "/api/v1/customers", params={"search": phone}, headers=admin_headers
        )
        customer_id = customers.json()[0]["id"]

        conversations = await client.get(
            f"/api/v1/customers/{customer_id}/conversations", headers=admin_headers
        )
        assert conversations.status_code == 200
        convo_list = conversations.json()
        assert len(convo_list) == 1
        assert convo_list[0]["is_lead_captured"] is True

        detail = await client.get(
            f"/api/v1/customers/{customer_id}/conversations/{convo_list[0]['id']}",
            headers=admin_headers,
        )
        assert detail.status_code == 200
        roles = [m["role"] for m in detail.json()["messages"]]
        assert "user" in roles and "ai" in roles


# ── Sales management + permissions matrix ────────────────────────────────────


class TestSalesManagement:
    @pytest.mark.asyncio
    async def test_sale_crud_and_awards(self, client):
        admin_headers = _auth(await _admin_token(client))
        sale_id, _ = await _create_sale(client, admin_headers)

        update = await client.patch(
            f"/api/v1/sales/{sale_id}",
            json={"title": "Chuyên viên KD", "work_shift_start": "08:30:00", "work_shift_end": "17:30:00"},
            headers=admin_headers,
        )
        assert update.status_code == 200
        assert update.json()["title"] == "Chuyên viên KD"

        award = await client.post(
            f"/api/v1/sales/{sale_id}/awards",
            json={"award_name": "Best Seller Q1", "awarded_at": "2026-03-31"},
            headers=admin_headers,
        )
        assert award.status_code == 201

        detail = await client.get(f"/api/v1/sales/{sale_id}", headers=admin_headers)
        assert detail.json()["awards"][0]["award_name"] == "Best Seller Q1"

        delete = await client.delete(f"/api/v1/sales/{sale_id}", headers=admin_headers)
        assert delete.status_code == 204

    @pytest.mark.asyncio
    async def test_assign_subdivisions_to_sale(self, client):
        admin_headers = _auth(await _admin_token(client))
        sale_id, _ = await _create_sale(client, admin_headers)

        # Lấy id 2 phân khu qua trick capture (public API trả slug, không trả id)
        capture = await client.post(
            "/api/v1/customers/capture",
            json={"full_name": "Tmp2", "phone": _phone(), "interested_subdivision_slug": "the-zenpark"},
        )
        detail = await client.get(
            f"/api/v1/customers/{capture.json()['customer_id']}", headers=admin_headers
        )
        subdivision_id = detail.json()["interested_subdivision"]["id"]

        response = await client.put(
            f"/api/v1/sales/{sale_id}/subdivisions",
            json={"subdivision_ids": [subdivision_id]},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert [s["id"] for s in response.json()["subdivisions"]] == [subdivision_id]

    @pytest.mark.asyncio
    async def test_permission_matrix_grant_and_revoke(self, client):
        admin_headers = _auth(await _admin_token(client))
        sale_id, sale_token = await _create_sale(client, admin_headers)

        # Chưa có quyền dashboard
        stats = await client.get("/api/v1/dashboard/stats", headers=_auth(sale_token))
        assert stats.status_code == 403

        grant = await client.put(
            f"/api/v1/sales/{sale_id}/permissions",
            json={"codes": ["dashboard.view"]},
            headers=admin_headers,
        )
        assert grant.status_code == 200
        stats = await client.get("/api/v1/dashboard/stats", headers=_auth(sale_token))
        assert stats.status_code == 200

        revoke = await client.put(
            f"/api/v1/sales/{sale_id}/permissions", json={"codes": []}, headers=admin_headers
        )
        assert revoke.status_code == 200
        stats = await client.get("/api/v1/dashboard/stats", headers=_auth(sale_token))
        assert stats.status_code == 403

    @pytest.mark.asyncio
    async def test_sale_updates_own_profile(self, client):
        admin_headers = _auth(await _admin_token(client))
        _, sale_token = await _create_sale(client, admin_headers)

        response = await client.patch(
            "/api/v1/auth/me",
            json={"full_name": "Sale Đổi Tên", "title": "Senior Sales"},
            headers=_auth(sale_token),
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Sale Đổi Tên"


# ── Dashboard + fallback rules ───────────────────────────────────────────────


class TestDashboardAndFallback:
    @pytest.mark.asyncio
    async def test_dashboard_stats_shape(self, client):
        admin_headers = _auth(await _admin_token(client))
        await client.post(
            "/api/v1/customers/capture", json={"full_name": "Khách Dash", "phone": _phone()}
        )
        response = await client.get("/api/v1/dashboard/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_customers"] >= 1
        assert data["new_today"] >= 1
        assert {item["label"] for item in data["status_funnel"]} == {
            "new", "contacted", "consulting", "visiting", "won", "lost",
        }
        assert "capture_rate" in data

    @pytest.mark.asyncio
    async def test_fallback_rule_crud_and_usage_in_chat(self, client):
        admin_headers = _auth(await _admin_token(client))
        keyword = f"kw-{uuid.uuid4().hex[:6]}"
        create = await client.post(
            "/api/v1/fallback-rules",
            json={"keyword": keyword, "response_message": "Trả lời cứng", "priority": 10},
            headers=admin_headers,
        )
        assert create.status_code == 201
        rule_id = create.json()["id"]

        session_id = str(uuid.uuid4())
        chat = await client.post(
            "/agent/chat",
            json={
                "messages": [{"role": "user", "content": f"cho hỏi {keyword} là gì"}],
                "session_id": session_id,
            },
        )
        assert chat.json()["response"] == "Trả lời cứng"

        delete = await client.delete(f"/api/v1/fallback-rules/{rule_id}", headers=admin_headers)
        assert delete.status_code == 204
