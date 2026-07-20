# Version 0.9.5 - Chat flow, UI handover form, and security hardening

Ngày thực hiện: 2026-07-01

## 1. Vấn đề được xử lý

Người dùng đăng nhập, mở chat và hỏi tư vấn nhưng gặp các lỗi:

- AI trả lời nối nhiều câu hỏi cũ, làm đoạn chat dài và khó hiểu.
- Câu hỏi follow-up như “còn phân khu nào khác ngoài Zenpark không” vẫn có thể bị trả lời fallback “Thông tin này hiện chưa có đủ nguồn đáng tin cậy...”.
- UI khu vực “Gặp Sales” và form tạo ticket bị vỡ hàng, input tràn, trải nghiệm giống form thô thay vì chat widget.
- `ReactMarkdown` phía client đang cho phép transform URL quá rộng, không cần thiết cho chat public.

## 2. Nguyên nhân

### 2.1. AI trả lời nối câu hỏi

Ở luồng khách đã đăng nhập:

```text
agent_routes.py -> load toàn bộ Message từ database -> agent.ainvoke(messages=history)
```

Trong khi đó `llm_node.py` chỉ convert các message role `user` thành `HumanMessage`, không đưa assistant messages vào. Kết quả là LLM nhận nhiều câu hỏi user liên tiếp và có xu hướng trả lời lại toàn bộ lịch sử.

### 2.2. Fallback thiếu context quá sớm

Một số câu tư vấn bình thường không phải dữ kiện nhạy cảm nhưng vẫn bị đi vào nhánh fallback do `insufficient_context`/citation verifier quá nghiêm.

### 2.3. UI form ticket chưa có CSS riêng

`chat-sales-bar` và `chat-lead-form` thiếu layout đầy đủ, khiến nút/form/input vỡ hàng trong khung chat nhỏ.

## 3. Phương án đã triển khai

### 3.1. Tách câu hỏi hiện tại khỏi lịch sử profile

Các file:

- `src/api/agent_routes.py`
- `src/agents/state.py`
- `src/agents/nodes/intent_node.py`
- `src/agents/nodes/llm_node.py`

Cách mới:

```text
messages = chỉ câu hỏi user mới nhất
profile_messages = lịch sử hội thoại dùng để extract budget/unit_type/purpose
```

Như vậy:

- LLM chỉ trả lời câu hỏi mới nhất.
- AI vẫn nhớ nhu cầu cũ thông qua `profile_messages`.
- Lịch sử chat vẫn được lưu đầy đủ trong database cho CRM/Admin.

### 3.2. Chỉ gửi câu hỏi user cuối vào LLM provider

`llm_node.py` giờ lấy `_last_user_text(state)` và chỉ tạo một `HumanMessage` cho câu hỏi mới nhất.

System prompt cũng được bổ sung quy tắc:

```text
Chỉ trả lời câu hỏi mới nhất của khách.
Không tóm tắt lại, không trả lời lại toàn bộ câu hỏi cũ trong lịch sử.
```

### 3.3. Fallback tư vấn thân thiện hơn

Khi provider LLM lỗi nhưng hệ thống có `zone_context` hoặc `recommended_zones`, AI sẽ trả lời tư vấn ngắn dựa trên phân khu/context thay vì fallback “không đủ nguồn”.

### 3.4. Sửa UI handover/ticket

Các file:

- `FE/src/components/chat-widget.tsx`
- `FE/src/app/globals.css`

Đã làm:

- Thêm layout riêng cho `.chat-sales-bar`.
- Thêm layout grid cho `.chat-lead-form`.
- Bỏ trường email khỏi form chat ticket để đúng flow tên + số điện thoại + ghi chú.
- Thêm `maxLength` cho tên, số điện thoại, ghi chú và input chat.
- Nút “Gặp Sales” không còn làm vỡ hàng.
- Form ticket co giãn tốt trong khung chat.

### 3.5. Security hardening nhẹ phía frontend

`ReactMarkdown` không còn cho phép mọi URL đi qua.

URL hợp lệ trong chat chỉ gồm:

- link nội bộ `/phan-khu/...`;
- `http://...`;
- `https://...`.

Các scheme nguy hiểm hoặc không cần thiết sẽ bị loại bỏ.

## 4. Cách test tự động đã chạy

### Backend lint

```bash
.\.venv\Scripts\ruff.exe check src\api\agent_routes.py src\agents\state.py src\agents\nodes\intent_node.py src\agents\nodes\llm_node.py src\agents\nodes\rag_node.py tests\test_agents\test_llm_fallback_policy.py --output-format concise
```

Kết quả:

```text
All checks passed!
```

### Backend tests

```bash
.\.venv\Scripts\python.exe -m pytest tests\test_agents\test_llm_fallback_policy.py tests\test_agents\test_rag_eval_regressions.py -q
```

Kết quả:

```text
10 passed
```

```bash
.\.venv\Scripts\python.exe -m pytest tests\test_agents\test_graph.py tests\test_agents\test_rag_scenario2.py -q
```

Kết quả:

```text
29 passed
```

### Frontend build

```bash
npm run build
```

Chạy trong thư mục `FE/`.

Kết quả:

```text
Compiled successfully
Finished TypeScript
Generated static pages successfully
```

## 5. Kịch bản tự test như một khách mua nhà

Nếu là khách mua nhà thật, mình sẽ test theo flow sau.

### Case 1: Chat tư vấn cơ bản

Input:

```text
tôi cần tư vấn căn 2PN cho gia đình có 2 con nhỏ
```

Kỳ vọng:

- AI hỏi thêm ngân sách/mục đích hoặc gợi ý nhóm phân khu phù hợp.
- Không mở form Sales ngay.
- Không trả fallback “không đủ nguồn”.

### Case 2: Follow-up không bị trả lời nối

Input tiếp theo:

```text
còn phân khu nào khác ngoài Zenpark không
```

Kỳ vọng:

- AI chỉ trả lời câu hỏi này.
- Không trả lời lại toàn bộ câu “tôi cần tư vấn căn 2PN...”.
- Có thể gợi ý The Pavilion, The Sapphire, Masteri Waterfront hoặc nhóm phân khu khác tùy context.

### Case 3: Hỏi dữ kiện cần Sales

Input:

```text
còn quỹ căn 2PN nào không, giá chốt hôm nay bao nhiêu
```

Kỳ vọng:

- AI không bịa giá/quỹ căn.
- AI mời để lại thông tin hoặc gặp Sales.
- Form Sales mở gọn, không vỡ UI.

### Case 4: Tạo ticket

Input form:

```text
Họ tên: Trần Thị Tuyết M
SĐT: 0912345678
Ghi chú: muốn xem 2PN cuối tuần
```

Kỳ vọng:

- Tạo ticket thành công.
- Không cần email.
- Admin CRM có lead/ticket tương ứng.

### Case 5: Security UI

Input thử:

```text
[click](javascript:alert(1))
```

Kỳ vọng:

- Link nguy hiểm không được render thành URL có thể click.
- Chat không crash.

## 6. Ghi chú còn nên theo dõi

- Chất lượng trả lời cuối cùng vẫn phụ thuộc LLM provider và data retrieval.
- Nếu production vẫn trả fallback cũ, cần kiểm tra image/tag đã build và deploy đúng version mới chưa.
- Nên tiếp tục bổ sung test API-level cho `/agent/chat` với authenticated customer để kiểm chứng database conversation + profile_messages trên môi trường test DB.
