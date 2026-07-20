# Spec: Lọc Lead & Sales Ticket CRM

## 1. Mục tiêu

Tính năng này biến hội thoại RAG chatbot thành một luồng CRM đơn giản cho đội Sales:

- Khách chủ động bấm **Gặp Sales** trong chat widget thì hệ thống mở form lấy tên, số điện thoại, email/ghi chú và tạo ticket.
- Khi khách để lại thông tin qua `POST /api/v1/leads`, hệ thống chấm điểm lead bằng LLM theo rubric bất động sản.
- Nếu LLM lỗi, timeout, trả JSON sai hoặc hết quota, hệ thống dùng rubric rule-based dự phòng để không mất lead.
- Ticket được biểu diễn bằng bản ghi `Lead` hiện có, trạng thái mặc định `new`, kèm metadata điểm số để Sales ưu tiên xử lý.

## 2. Phạm vi

Trong phạm vi hiện tại:

- Không tạo bảng `tickets` riêng. `Lead` chính là sales ticket tối giản.
- Không tự tạo ticket từ chat nếu chưa có số điện thoại. Chat chỉ bật CTA/form khi `trigger_handover=true`.
- Không tích hợp CRM ngoài như HubSpot/Salesforce.
- Không phân công sale tự động theo workload; admin dashboard hiện có vẫn xử lý phân công/trạng thái.

## 3. Rubric chấm điểm 0-100

| Nhóm tiêu chí | Điểm tối đa | Ý nghĩa |
|---|---:|---|
| Ngân sách | 30 | Có ngân sách rõ và đủ khả năng mua căn Ocean Park. Mốc từ 2 tỷ trở lên là tín hiệu tốt. |
| Thời gian/độ khẩn cấp | 20 | Muốn mua ngay, xem nhà sớm, trong 1-3 tháng được ưu tiên cao. |
| Mục đích mua | 15 | Ở thật, đầu tư, cho thuê, mua cho gia đình càng rõ càng tốt. |
| Loại căn/nhu cầu sản phẩm | 10 | Có loại căn, phân khu, mã căn hoặc yêu cầu cụ thể. |
| Bối cảnh gia đình/life stage | 10 | Vợ chồng trẻ, mới cưới, có con, chuyển nhà, gần trường/làm việc. |
| Sẵn sàng liên hệ Sales | 15 | Bấm Gặp Sales, hỏi đặt cọc, lịch xem nhà, quỹ căn thật, để lại liên hệ. |

Quy đổi:

- `HOT`: `numeric_score >= 70`, hoặc có tín hiệu mua rất rõ.
- `WARM`: `numeric_score` từ 40 đến 69.
- `COLD`: `numeric_score < 40`.
- `handover_recommended=true` khi điểm đạt ngưỡng 70 hoặc khách chủ động bấm **Gặp Sales**.

## 4. API contract

### POST `/api/v1/leads`

Tạo lead/ticket CRM. Payload mở rộng:

```json
{
  "name": "Nguyen Van A",
  "phone": "0912345678",
  "email": "a@example.com",
  "session_id": "uuid-session",
  "chat_history": [
    {"role": "user", "content": "Tôi muốn gặp Sales để xem căn 2PN"}
  ],
  "user_profile": {
    "budget": 3000000000,
    "purpose": "ở thật",
    "unit_type": "2PN",
    "timeline": "cuối tuần này",
    "family_size": 2,
    "life_stage": "vợ chồng trẻ mới cưới",
    "notes": "Muốn xem nhà cuối tuần"
  },
  "manual_sales_request": true
}
```

Response mở rộng:

```json
{
  "lead_id": "uuid",
  "score": "HOT",
  "numeric_score": 85,
  "score_reason": "Khách có ngân sách rõ, muốn xem nhà sớm và chủ động gặp Sales.",
  "scoring_breakdown": {
    "budget": 30,
    "timeline": 20,
    "purpose": 15,
    "unit_type": 10,
    "life_stage": 10,
    "contact_readiness": 15
  },
  "handover_recommended": true,
  "ticket_created": true,
  "ticket_source": "manual_sales_click",
  "message": "Sales sẽ liên hệ bạn trong thời gian sớm nhất!"
}
```

### POST `/agent/lead-score`

Chấm điểm thử nhưng không lưu DB. Response có thêm:

- `numeric_score`
- `scoring_breakdown`
- `handover_recommended`

## 5. Luồng frontend

1. Khách chat bình thường.
2. Nếu AI trả `trigger_handover=true`, chat widget tự mở form tạo ticket.
3. Khách cũng có thể bấm nút **Gặp Sales** bất kỳ lúc nào.
4. Form gửi `POST /api/v1/leads` với `manual_sales_request=true`, `session_id` và `chat_history`.
5. Backend migrate lịch sử chat theo `session_id`, chấm điểm lead, trả score và tạo ticket.
6. Chat widget thông báo ticket đã tạo cùng mức ưu tiên.

## 6. Acceptance criteria

- Khách bấm **Gặp Sales** và nhập tên/SĐT hợp lệ thì tạo `Lead` trạng thái `new`.
- Lead tạo từ nút manual có `ticket_source="manual_sales_click"`.
- Lead response có `numeric_score`, `scoring_breakdown`, `handover_recommended`, `ticket_created`.
- LLM scoring trả JSON hợp lệ thì dùng điểm LLM sau khi normalize.
- LLM lỗi hoặc trả JSON/field sai thì fallback rule-based, không lộ lỗi nội bộ cho client.
- Admin API `GET /api/v1/leads/{id}` trả lại metadata ticket/scoring.
- Test unit/API/failure có mock LLM, không phụ thuộc provider thật.

## 7. Kiểm thử

Test đã thêm/cập nhật:

- Unit: `_rule_based_detail` chấm HOT cho khách bấm Gặp Sales, COLD cho khách chỉ tìm hiểu.
- API integration: `manual_sales_request=true` tạo ticket metadata và admin retrieve được.
- Failure: LLM trả structured field sai vẫn normalize/fallback an toàn.

Lệnh kiểm thử khuyến nghị:

```powershell
python -m pytest tests\test_unit\test_intent_and_scoring.py tests\test_failure\test_graceful_degradation.py tests\test_api\test_integration.py -q
```

## 8. Review kiến trúc và rủi ro

- **Không có bảng ticket riêng:** phù hợp demo CRM đơn giản, nhưng khi cần SLA, assignment history, audit log hoặc nhiều ticket trên một lead thì nên tách bảng `sales_tickets`.
- **Chưa tự tạo ticket nếu thiếu số điện thoại:** đây là lựa chọn đúng về vận hành. Ticket không có liên hệ sẽ khó follow-up; chat chỉ mở CTA/form.
- **Metadata scoring lưu trong `user_profile_json`:** tránh migration trong phase hiện tại. Nếu production hóa, nên thêm cột riêng `numeric_score`, `ticket_source`, `handover_recommended` để query/filter hiệu quả.
- **Frontend admin hiện có dấu hiệu dùng contract `/admin/leads` khác `/api/v1/leads`:** cần đồng bộ nếu muốn dashboard hiển thị trực tiếp `numeric_score` và `ticket_source`.
- **LLM prompt là code:** rubric đã version trong `lead_scorer.py`, cần regression test trước khi chỉnh prompt.
