"""Tests luồng handover + tự phân công sale (Mục 5.3, 6.4)."""

import uuid
from unittest.mock import patch

import pytest


def _phone() -> str:
    return f"09{str(uuid.uuid4().int)[:8]}"


async def _admin_headers(client) -> dict:
    from src.config import get_settings

    settings = get_settings()
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.asyncio
async def test_hot_detected_triggers_handover_and_autoassign(client):
    admin_headers = await _admin_headers(client)

    # Tạo sale phụ trách the-zenpark
    email = f"sale-{uuid.uuid4().hex[:8]}@x.vn"
    sale = await client.post(
        "/api/v1/sales",
        json={"email": email, "full_name": "Sale Zenpark", "password": "password123"},
        headers=admin_headers,
    )
    sale_id = sale.json()["id"]

    # Lấy id phân khu the-zenpark
    capture_tmp = await client.post(
        "/api/v1/customers/capture",
        json={"full_name": "Tmp", "phone": _phone(), "interested_subdivision_slug": "the-zenpark"},
    )
    tmp_detail = await client.get(
        f"/api/v1/customers/{capture_tmp.json()['customer_id']}", headers=admin_headers
    )
    zenpark_id = tmp_detail.json()["interested_subdivision"]["id"]
    await client.put(
        f"/api/v1/sales/{sale_id}/subdivisions",
        json={"subdivision_ids": [zenpark_id]},
        headers=admin_headers,
    )

    # Khách chat, capture, rồi agent trả detected hot
    session_id = str(uuid.uuid4())
    phone = _phone()
    with patch("src.api.agent_routes.agent.ainvoke") as mock_agent:
        mock_agent.return_value = {
            "response": "Chào anh chị",
            "intent": "consult",
            "trigger_handover": False,
            "recommended_zones": [],
            "citations": [],
        }
        await client.post(
            "/agent/chat",
            json={"messages": [{"role": "user", "content": "Quan tâm The Zenpark"}], "session_id": session_id},
        )
    await client.post(
        "/api/v1/customers/capture",
        json={
            "full_name": "Khách Hot",
            "phone": phone,
            "session_id": session_id,
            "interested_subdivision_slug": "the-zenpark",
        },
    )

    with patch("src.api.agent_routes.agent.ainvoke") as mock_agent:
        mock_agent.return_value = {
            "response": "Em sẽ kết nối sales ngay ạ",
            "intent": "consult",
            "trigger_handover": False,
            "recommended_zones": [],
            "citations": [],
            "detected": {
                "customer_type": "real_need",
                "temperature": "hot",
                "lead_score": 70,
                "score_delta": 30,
                "interested_subdivision": "the-zenpark",
                "budget_range": [None, None],
                "unit_type": "2PN",
            },
        }
        response = await client.post(
            "/agent/chat",
            json={
                "messages": [{"role": "user", "content": "Tôi muốn xem nhà tuần này"}],
                "session_id": session_id,
            },
        )

    data = response.json()
    assert data["trigger_handover"] is True
    assert data["detected"]["temperature"] == "hot"

    # Khách được phân công cho một sale phụ trách Zenpark (round-robin theo tải,
    # nên có thể là sale khác cũng phụ trách Zenpark do test khác tạo ra).
    all_sales = await client.get("/api/v1/sales", headers=admin_headers)
    zenpark_sale_ids = {
        s["id"]
        for s in all_sales.json()
        if any(sub["id"] == zenpark_id for sub in s["subdivisions"])
    }
    assert sale_id in zenpark_sale_ids
    customers = await client.get(
        "/api/v1/customers", params={"search": phone}, headers=admin_headers
    )
    customer = customers.json()[0]
    assert customer["assigned_sale"]["id"] in zenpark_sale_ids
    assert customer["temperature"] == "hot"
    assert customer["lead_score"] == 70
    assert customer["customer_type"] == "real_need"
    assert customer["status"] == "contacted"


@pytest.mark.asyncio
async def test_capture_bonus_score_applied(client):
    session_id = str(uuid.uuid4())
    phone = _phone()
    with patch("src.api.agent_routes.agent.ainvoke") as mock_agent:
        mock_agent.return_value = {
            "response": "OK",
            "intent": "consult",
            "trigger_handover": False,
            "recommended_zones": [],
            "citations": [],
        }
        await client.post(
            "/agent/chat",
            json={"messages": [{"role": "user", "content": "Hỏi về dự án"}], "session_id": session_id},
        )
    await client.post(
        "/api/v1/customers/capture",
        json={"full_name": "Khách Bonus", "phone": phone, "session_id": session_id},
    )

    admin_headers = await _admin_headers(client)
    customers = await client.get(
        "/api/v1/customers", params={"search": phone}, headers=admin_headers
    )
    customer = customers.json()[0]
    assert customer["lead_score"] == 15  # bonus để lại SĐT sớm
    assert customer["temperature"] == "cold"


@pytest.mark.asyncio
async def test_capture_inherits_anonymous_score(client):
    """Điểm tích lũy khi còn ẩn danh phải được kế thừa vào customer khi capture."""
    session_id = str(uuid.uuid4())
    phone = _phone()
    with patch("src.api.agent_routes.agent.ainvoke") as mock_agent:
        mock_agent.return_value = {
            "response": "OK",
            "intent": "consult",
            "trigger_handover": False,
            "recommended_zones": [],
            "citations": [],
            "detected": {
                "customer_type": "unknown",
                "temperature": "warm",
                "lead_score": 30,
                "score_delta": 30,
                "interested_subdivision": None,
                "budget_range": [None, None],
                "unit_type": None,
            },
        }
        await client.post(
            "/agent/chat",
            json={"messages": [{"role": "user", "content": "Ngân sách 3 tỷ"}], "session_id": session_id},
        )
    await client.post(
        "/api/v1/customers/capture",
        json={"full_name": "Khách Kế Thừa", "phone": phone, "session_id": session_id},
    )

    admin_headers = await _admin_headers(client)
    customers = await client.get(
        "/api/v1/customers", params={"search": phone}, headers=admin_headers
    )
    customer = customers.json()[0]
    assert customer["lead_score"] == 45  # 30 điểm ẩn danh + 15 bonus capture
    assert customer["temperature"] == "warm"


