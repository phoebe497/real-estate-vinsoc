"""Tests cho profile_node — rubric chấm điểm & phân loại (Mục 6.3)."""

import pytest

from src.agents.nodes.profile_node import (
    classify_customer_type,
    compute_score_delta,
    profile_node,
    temperature_for,
)


class TestScoreDelta:
    def test_visit_request_scores_30(self):
        delta, signals = compute_score_delta("Tôi muốn đặt lịch xem nhà cuối tuần", [], "consult")
        assert signals.get("visit_request") == 30
        assert delta >= 30

    def test_meet_sale_scores_25(self):
        delta, signals = compute_score_delta("Cho tôi gặp sale tư vấn trực tiếp", [], "handover")
        assert signals.get("meet_sale") == 25

    def test_deposit_scores_25(self):
        _, signals = compute_score_delta("Thủ tục đặt cọc như thế nào?", [], "handover")
        assert signals.get("deposit_intent") == 25

    def test_budget_scores_10(self):
        _, signals = compute_score_delta("Ngân sách của tôi khoảng 3 tỷ", [], "consult")
        assert signals.get("budget_discussed") == 10

    def test_zone_comparison_scores_8(self):
        _, signals = compute_score_delta(
            "So sánh The Zenpark và The Sapphire giúp tôi", [], "consult"
        )
        assert signals.get("zone_comparison") == 8

    def test_zone_focus_repeated_scores_15(self):
        history = ["The Zenpark có mấy tòa?", "The Zenpark bàn giao chưa?"]
        _, signals = compute_score_delta("The Zenpark còn căn 2PN không?", history, "consult")
        assert signals.get("zone_focus") == 15

    def test_off_topic_penalty(self):
        delta, signals = compute_score_delta("Hôm nay thời tiết thế nào?", [], "out_of_scope")
        assert signals.get("off_topic") == -10
        assert delta == -10

    def test_generic_question_penalty(self):
        delta, signals = compute_score_delta("Cho hỏi chút nhé", [], "consult")
        assert signals.get("generic_question") == -5

    def test_greeting_no_penalty(self):
        delta, _ = compute_score_delta("Xin chào", [], "greeting")
        assert delta == 0


class TestTemperature:
    def test_thresholds(self):
        assert temperature_for(55) == "hot"
        assert temperature_for(54) == "warm"
        assert temperature_for(25) == "warm"
        assert temperature_for(24) == "cold"
        assert temperature_for(0) == "cold"


class TestCustomerType:
    def test_investor(self):
        texts = ["Tỷ suất cho thuê ở đây bao nhiêu?", "Tôi muốn đầu tư lướt sóng"]
        assert classify_customer_type(texts) == "investor"

    def test_real_need(self):
        texts = ["Gia đình tôi có con nhỏ, gần trường không?", "Mua để ở lâu dài"]
        assert classify_customer_type(texts) == "real_need"

    def test_ghost_off_topic_spam(self):
        texts = ["Kể chuyện cười đi", "Bạn là bot à?", "1+1 bằng mấy"]
        assert classify_customer_type(texts) == "ghost"

    def test_unknown_when_insufficient(self):
        assert classify_customer_type(["The Zenpark giá bao nhiêu?"]) == "unknown"


class TestProfileNode:
    @pytest.mark.asyncio
    async def test_accumulates_score_across_turns(self):
        result = await profile_node(
            {
                "messages": [{"role": "user", "content": "Tôi muốn đặt lịch xem nhà The Zenpark"}],
                "profile_messages": [
                    {"role": "user", "content": "Ngân sách 3 tỷ mua The Zenpark"},
                    {"role": "user", "content": "Tôi muốn đặt lịch xem nhà The Zenpark"},
                ],
                "intent": "consult",
                "current_lead_score": 20,
                "user_profile": {"budget": 3_000_000_000, "unit_type": "2PN"},
                "recommended_zones": [
                    {"name": "The Zenpark", "slug": "the-zenpark", "match_reason": "", "price_range": "", "design_style": ""}
                ],
            }
        )
        detected = result["detected"]
        # 20 + 30 (visit) + 15 (zone focus) = 65 → hot
        assert detected["lead_score"] == 65
        assert detected["temperature"] == "hot"
        assert detected["score_delta"] == 45
        assert detected["interested_subdivision"] == "the-zenpark"
        assert detected["unit_type"] == "2PN"
        assert detected["budget_range"] == [3_000_000_000, 3_000_000_000]

    @pytest.mark.asyncio
    async def test_score_clamped_to_bounds(self):
        result = await profile_node(
            {
                "messages": [{"role": "user", "content": "Chuyện linh tinh ngoài lề"}],
                "profile_messages": [{"role": "user", "content": "Chuyện linh tinh ngoài lề"}],
                "intent": "out_of_scope",
                "current_lead_score": 5,
            }
        )
        assert result["detected"]["lead_score"] == 0
