# Version 0.9.4 - AI chat citation fallback fix

Ngày thực hiện: 2026-06-30

## 1. Vấn đề

Chat AI có thể nhận câu hỏi bình thường như:

```text
tôi cần 2PN thì phân khu nào hợp lý
ok tôi cần tư vấn về phân khu zenpark
```

nhưng lại trả lời:

```text
Thông tin này hiện chưa có đủ nguồn đáng tin cậy trong dữ liệu. Vui lòng liên hệ Sales để được xác nhận chi tiết.
```

Điều này làm AI gần như không tư vấn được, dù hệ thống vẫn có dữ liệu phân khu/context.

## 2. Nguyên nhân chính

Luồng hiện tại là:

```text
intent_node -> rag_node -> llm_node -> citation_verifier
```

Các điểm gây lỗi:

- `rag_node` đánh dấu `status="insufficient_context"` quá sớm khi retrieval không lấy được chunk đủ mạnh.
- `llm_node` trước đó có xu hướng chặn ngay nếu thấy `insufficient_context`.
- `citation_verifier` được dùng quá nghiêm: câu trả lời tư vấn thông thường cũng có thể bị thay bằng fallback nếu thiếu citation.
- Khi LLM provider lỗi hoặc không phản hồi, fallback cũ chỉ dựa vào `retrieved_chunks`; nếu không có chunk thì bỏ qua `recommended_zones/zone_context` và trả câu “không đủ nguồn”.

## 3. Phương án đã áp dụng

### 3.1. Nới điều kiện RAG cho câu tư vấn bình thường

File: `src/agents/nodes/rag_node.py`

Nếu intent là `consult`, `zone_match`, `price_query` và hệ thống đã có project/zone context đủ dùng, `rag_node` không còn đánh dấu thiếu context quá sớm.

Mục tiêu: các câu hỏi tư vấn như “2PN khu nào hợp lý?” vẫn đi tiếp sang bước sinh câu trả lời.

### 3.2. Chỉ strict citation với nhóm dữ kiện nhạy cảm

File: `src/agents/nodes/llm_node.py`

Thêm hàm `_requires_strict_citation(...)`.

Chỉ bắt buộc fallback nghiêm khi câu hỏi/câu trả lời liên quan:

- giá chốt, giá hiện hành;
- quỹ căn, bảng hàng, mã căn, căn cụ thể;
- đặt cọc/giữ chỗ;
- pháp lý, sổ đỏ/sổ hồng, hợp đồng;
- chính sách, ưu đãi, lãi suất.

Với câu tư vấn thông thường, nếu citation verifier báo thiếu citation thì vẫn giữ câu trả lời và set `status="ok"`.

### 3.3. Fallback hữu ích khi LLM provider lỗi

File: `src/agents/nodes/llm_node.py`

Thêm `_fallback_response_from_zone_context(...)`.

Nếu OpenRouter/OpenAI lỗi nhưng `recommended_zones` hoặc `zone_context` vẫn có dữ liệu, hệ thống sẽ trả một câu tư vấn ngắn dựa trên phân khu thay vì trả “không đủ nguồn”.

### 3.4. Chuẩn hóa citation token của recommended zones

File: `src/agents/nodes/llm_node.py`

Các chunk giả tạo từ `recommended_zones` trước đây dùng slug làm citation token. `citation_verifier` chỉ hiểu dạng `C1`, `C2`, nên đã đổi sang token hợp lệ.

### 3.5. Sửa format trạng thái phân khu

File: `src/agents/nodes/llm_node.py`

Sửa `_polish_response_format(...)` để xử lý cả Unicode chuẩn và dữ liệu mojibake cũ cho các nhãn như:

- `handed_over`
- `under_construction`
- `not_launched`
- `planning`

Mục tiêu: câu trả lời hiển thị sạch hơn, không lộ nhãn kỹ thuật như `Trạng thái: handed_over`.

## 4. Test đã thêm

File mới: `tests/test_agents/test_llm_fallback_policy.py`

Test bao phủ:

1. Nếu LLM provider lỗi nhưng có zone context/recommended zones, AI phải trả lời tư vấn hữu ích, không trả generic insufficient context.
2. Nếu citation verifier báo thiếu citation cho câu tư vấn không nhạy cảm, câu trả lời vẫn được giữ lại.

## 5. Cách test

Chạy lint các file liên quan:

```bash
.\.venv\Scripts\ruff.exe check src\agents\nodes\llm_node.py src\agents\nodes\rag_node.py tests\test_agents\test_llm_fallback_policy.py tests\test_agents\test_rag_eval_regressions.py --output-format concise
```

Chạy test mục tiêu:

```bash
.\.venv\Scripts\python.exe -m pytest tests\test_agents\test_llm_fallback_policy.py tests\test_agents\test_rag_eval_regressions.py -q
```

Kết quả local:

```text
All checks passed!
9 passed
```

## 6. Cách test thủ công trên local

Sau khi build/chạy lại local:

```bash
docker compose up -d --build
```

Mở client và thử chat:

```text
ok tôi cần tư vấn về phân khu zenpark
tôi cần 2PN thì phân khu nào hợp lý
gia đình tôi có 2 con nhỏ nên chọn phân khu nào
```

Kỳ vọng:

- AI trả lời tư vấn được, không trả fallback “không đủ nguồn” cho câu hỏi bình thường.
- AI vẫn mời gặp Sales hoặc fallback an toàn nếu hỏi giá chốt/quỹ căn/mã căn/đặt cọc/pháp lý.

## 7. Ghi chú

`citation_verifier` vẫn cần thiết. Nó không phải AI mà là lớp kiểm tra an toàn sau LLM để:

- xóa citation/link giả;
- render citation hợp lệ;
- chặn các câu trả lời nhạy cảm nếu thiếu nguồn phù hợp.

Thay đổi lần này không bỏ verifier, chỉ điều chỉnh phạm vi áp dụng để AI không bị “câm” với câu hỏi tư vấn thông thường.
