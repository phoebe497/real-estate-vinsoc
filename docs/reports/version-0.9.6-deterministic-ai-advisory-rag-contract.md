# Version 0.9.6 - Deterministic AI Advisory & RAG Contract

Ngày thực hiện: 2026-07-01

## 1. Bối cảnh

Sau khi test luồng chat thực tế, AI còn các lỗi nghiêm trọng:

- Với câu hỏi tư vấn bình thường, bot trả lời fallback: “Thông tin này hiện chưa có đủ nguồn...”.
- Câu hỏi có đủ nhu cầu như gia đình 4 người, 2 con học cấp 2, ngân sách 4 tỷ vẫn không ra tư vấn rõ ràng.
- Citation verifier chặn cả những câu tư vấn tổng quan, dù dữ liệu dự án vẫn có context đủ để trả lời.
- LLM có nguy cơ bịa phân khu không thuộc dữ liệu dự án nếu prompt/retrieval không đủ chặt.
- Lịch sử chat có thể khiến model trả lời nối lại các câu hỏi cũ.

Nguyên nhân chính không nằm ở OpenRouter/OpenAI riêng lẻ, cũng không chỉ nằm ở việc có hay chưa có vectorDB. Vấn đề là luồng RAG chưa có “business contract” rõ ràng giữa:

```text
intent/profile extraction
-> retrieval/recommendation
-> context quality gate
-> answer planning
-> LLM/verifier
```

Vì vậy ở phiên bản này tôi bổ sung một lớp deterministic advisory response để các case tư vấn quan trọng có kết quả ổn định trước khi phụ thuộc vào LLM.

## 2. Công việc đã làm

### 2.1. Thiết kế lại AI/RAG contract

Tạo file:

- `docs/report_AI/AI_RAG_REARCHITECTURE_PLAN_2026_07_01.md`

Nội dung chính:

- Mục tiêu AI phải trả lời rõ ràng dù đang dùng `legacy` context hay sau này chuyển sang `pgvector`.
- Tách rõ factual facts và sales-sensitive facts.
- Chỉ yêu cầu strict citation với các thông tin nhạy cảm như giá chốt, quỹ căn, mã căn, đặt cọc, pháp lý, chính sách.
- Với tư vấn lựa chọn phân khu theo profile, dùng deterministic template để tránh fallback/hallucination.

### 2.2. Sửa intent/profile extraction

File:

- `src/agents/nodes/intent_node.py`
- `src/agents/state.py`

Thay đổi:

- Thêm `school_need` vào `UserProfile`.
- Extract profile từ `profile_messages`, không ép LLM phải đọc/trả lời lại toàn bộ lịch sử.
- Fix lỗi câu “gia đình 4 người, có 2 con” bị hiểu thành `family_size=2`; hiện lấy số lớn nhất là `4`.
- Nhận diện nhu cầu trường học/con nhỏ qua các cụm như `con nhỏ`, `cấp 2`, `trường`, `Vinschool`.
- Nếu gia đình từ 3 người trở lên và chưa có mục đích mua, mặc định tư vấn theo hướng `ở thật`.

### 2.3. Sửa scoring RAG/recommendation

File:

- `src/agents/nodes/rag_node.py`

Thay đổi:

- Với gia đình 4 người, hệ thống ưu tiên các loại căn `2PN+1`, `3PN`, `2PN`.
- Tính khoảng giá theo loại căn phù hợp với profile, không lấy min tổng toàn phân khu.
- Tránh gợi ý sai vì một phân khu có Studio/1PN rẻ nhưng căn phù hợp gia đình lại vượt ngân sách.
- Cộng điểm cho phân khu có căn phù hợp gia đình và tiện ích giáo dục.
- Không để trạng thái `insufficient_context` nếu vẫn có project context đủ dùng cho câu hỏi tư vấn tổng quan.

### 2.4. Thêm deterministic advisory response

File:

- `src/agents/nodes/llm_node.py`

Thay đổi:

- Nếu RAG đã chọn được phân khu và profile đủ rõ, backend tự dựng câu trả lời tư vấn:
  - tóm tắt nhu cầu;
  - liệt kê 1-3 lựa chọn phù hợp;
  - nêu lý do;
  - ghi rõ giá là tham khảo;
  - không xác nhận giá chốt/quỹ căn realtime.
- Lớp này chạy trước khi gọi LLM để giảm phụ thuộc vào chất lượng model.
- Citation verifier không còn chặn nhầm câu tư vấn thông thường.
- LLM chỉ nhận latest user message để tránh trả lời nối lại toàn bộ lịch sử cũ.

### 2.5. Thêm regression test cho tình huống khách hàng thật

File:

- `tests/test_agents/test_customer_advisory_scenarios.py`

Case test:

```text
Gia đình tôi 4 người, có 2 con nhỏ học cấp 2.
Tài chính tối đa tầm 4 tỷ vậy thì lựa chọn nào sẽ phù hợp?
```

Kỳ vọng:

- Extract đúng `budget=4_000_000_000`.
- Extract đúng `family_size=4`.
- Extract đúng `school_need=True`.
- Có phân khu hợp lệ từ dữ liệu dự án.
- Response không fallback “Thông tin này hiện chưa...”.
- Response có cấu trúc tư vấn rõ ràng.
- Không bịa các phân khu ngoài dữ liệu như The Venice, The Milan, The Manhattan.

## 3. Kết quả kiểm thử

Đã chạy lint:

```powershell
.\.venv\Scripts\ruff.exe check src\agents\state.py src\agents\nodes\intent_node.py src\agents\nodes\rag_node.py src\agents\nodes\llm_node.py tests\test_agents\test_customer_advisory_scenarios.py tests\test_agents\test_llm_fallback_policy.py --output-format concise
```

Kết quả:

```text
All checks passed!
```

Đã chạy test mục tiêu:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_agents\test_customer_advisory_scenarios.py tests\test_agents\test_llm_fallback_policy.py tests\test_agents\test_rag_eval_regressions.py -q
```

Kết quả:

```text
11 passed
```

Đã chạy test scenario RAG từng có lỗi import:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_agents\test_rag_scenario2.py -q
```

Kết quả:

```text
18 passed
```

## 4. Cách test thủ công

### 4.1. Test local bằng Docker

Chạy lại môi trường local:

```powershell
docker compose down
docker compose up -d --build
```

Mở:

```text
http://127.0.0.1:3000
```

Đăng nhập user, mở chat và hỏi:

```text
Gia đình tôi 4 người, có 2 con nhỏ học cấp 2. Tài chính tối đa tầm 4 tỷ vậy thì lựa chọn nào sẽ phù hợp?
```

Kết quả mong muốn:

- Bot không trả lời “Thông tin này hiện chưa có đủ nguồn...”.
- Bot tóm tắt đúng nhu cầu gia đình 4 người, ngân sách 4 tỷ.
- Bot đưa ra phân khu trong dữ liệu dự án.
- Bot nói rõ giá chỉ là tham khảo, không phải giá chốt/quỹ căn realtime.
- Bot không tự bịa The Venice/The Milan/The Manhattan nếu các phân khu này không nằm trong dữ liệu.

### 4.2. Test trực tiếp backend

Nếu muốn test API:

```powershell
curl -X POST http://localhost:8000/agent/chat `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"Gia đình tôi 4 người, có 2 con nhỏ học cấp 2. Tài chính tối đa tầm 4 tỷ vậy thì lựa chọn nào sẽ phù hợp?\"}"
```

Nếu endpoint yêu cầu auth/session theo cấu hình hiện tại, test qua giao diện frontend sẽ dễ hơn.

## 5. Giới hạn còn lại

Phiên bản này chưa biến toàn bộ hệ thống thành vectorDB-first. Nó làm cho output tư vấn ổn định ngay cả khi đang dùng legacy retrieval.

Những phần nên làm tiếp:

1. Chuẩn hóa `knowledge_chunks` cho từng phân khu/sản phẩm/tiện ích theo schema cố định.
2. Nếu dùng Supabase/pgvector thật, cần kiểm tra ingestion pipeline:
   - dữ liệu nào được vector hóa;
   - chunk id/source/citation có lưu đủ không;
   - retrieval top-k có trả đúng phân khu không.
3. Tạo bộ eval 20-30 câu hỏi khách hàng từ file tình huống để đo chất lượng định kỳ.
4. Thêm answer planner cho các nhóm intent:
   - so sánh phân khu;
   - tư vấn theo ngân sách;
   - pháp lý;
   - quy trình mua;
   - handover/sales ticket.

## 6. Kết luận

Phiên bản 0.9.6 đã xử lý lõi của lỗi chat hiện tại: RAG có dữ liệu nhưng AI vẫn fallback hoặc trả lời sai. Hệ thống giờ có một lớp tư vấn quyết định bằng dữ liệu nội bộ trước khi phụ thuộc LLM, giúp câu trả lời ổn định hơn, ít bịa hơn và phù hợp hơn với nghiệp vụ bán hàng bất động sản.
