# Version 0.9.1 - AI data adapter and chunk-based RAG

Ngày thực hiện: 2026-06-27

## Mục tiêu

Triển khai theo báo cáo `docs/ai_agent_data_agent_audit_2026-06-27.md`: sửa nguyên nhân AI trả lời sai do RAG chưa đọc đúng `cleaned_data` và chưa dùng `ai_knowledge_chunks.json`.

Phiên bản này chưa dùng embedding/vector DB. Mục tiêu là làm retrieval/context đúng trước, để AI trả lời dựa trên dữ liệu dự án đã review.

## Công việc đã thực hiện

### 1. Làm lại data adapter cho `cleaned_data`

File thay đổi:

- `src/services/vinhomes_data.py`

Đã thay adapter cũ bằng adapter mới:

- đọc `cleaned_data/cleaned_apartment_zones.json`;
- normalize 12 phân khu thành runtime schema cho Agent;
- expose đầy đủ:
  - `apartment_specs`;
  - `unit_types`;
  - `total_price_range_billion`;
  - `internal_amenities`;
  - `external_amenities`;
  - `sales_policies`;
  - `handover_standard`;
  - `legal_status`;
  - project overview fallback.

Trước đây context bị thiếu giá và thường hiện:

```text
Giá tham khảo: ?-? tỷ
Dự án: None
```

Sau thay đổi, context có thể chứa thông tin cụ thể như:

```text
2PN: diện tích 64 - 70m2, giá 3,0 - 3,5 tỷ
```

### 2. Thêm keyword/chunk retriever

File mới:

- `src/services/knowledge_retriever.py`

Retriever mới đọc:

```text
cleaned_data/ai_knowledge_chunks.json
```

và retrieve theo:

- phân khu/slug/name;
- topic:
  - `apartment_specs`;
  - `internal_amenities`;
  - `external_amenities`;
  - `sales_policies`;
  - `location`;
  - `overview`;
- keyword overlap.

Ví dụ:

```text
The Zenpark căn 2PN giá bao nhiêu?
```

sẽ ưu tiên chunk:

```text
the-zenpark / apartment_specs
```

### 3. Cập nhật RAG node

File thay đổi:

- `src/agents/nodes/rag_node.py`

Đã cập nhật:

- scoring theo giá/unit type từ cleaned data;
- ưu tiên phân khu được user nhắc trực tiếp;
- thêm chunk context vào prompt với source label:

```text
[source: the-zenpark/apartment_specs]
```

- không còn phụ thuộc cứng vào `matching_rules` rỗng;
- vẫn giữ flow LangGraph hiện tại.

### 4. Cập nhật recommender endpoint

File thay đổi:

- `src/services/recommender.py`

Endpoint `/agent/recommend` giờ dùng price ranges và unit types từ cleaned data thay vì schema cũ.

### 5. Thêm test chất lượng retrieval

File mới:

- `tests/test_agents/test_retrieval_quality.py`

Test mới kiểm tra:

- data adapter expose đúng giá `The Zenpark / 2PN`;
- trạng thái giá chưa cập nhật được giữ nguyên, không bị convert sai;
- retriever detect đúng slug/topic;
- RAG context dùng đúng chunk `the-zenpark/apartment_specs`;
- recommendation dùng cleaned price ranges.

## Kết quả kiểm tra

Đã chạy trong backend Docker container:

```bash
docker compose run --rm --no-deps backend ruff check src tests
```

Kết quả:

```text
All checks passed!
```

```bash
docker compose run --rm --no-deps backend python -m pytest -q
```

Kết quả:

```text
146 passed
```

## Cách test thủ công

Sau khi rebuild/restart backend:

```bash
docker compose up -d --build
```

Test endpoint recommend:

```bash
curl -X POST http://localhost:8000/agent/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "budget": 3000000000,
    "unit_type": "2PN",
    "purpose": "ở thật",
    "top_k": 5
  }'
```

Kỳ vọng:

- response không còn toàn `?-? tỷ`;
- có các phân khu có `2PN`;
- reason nhắc ngân sách/loại căn rõ hơn.

Test chat:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "manual-v0-9-1",
    "messages": [
      {
        "role": "user",
        "content": "The Zenpark căn 2PN giá bao nhiêu và có tiện ích gì?"
      }
    ]
  }'
```

Kỳ vọng:

- HTTP 200;
- AI có cơ sở trả về giá 2PN The Zenpark theo data;
- nếu nhắc giá phải nói là giá tham khảo;
- không tư vấn quỹ căn/căn cụ thể.

## Giới hạn còn lại

Phiên bản này chưa làm:

- Supabase pgvector;
- embedding;
- semantic search;
- RAGAS/evaluation bằng LLM;
- sync database catalog khi `cleaned_data` đổi và DB đã seed cũ.

Đây là chủ ý: theo báo cáo audit, cần sửa data adapter/retrieval đúng trước khi đưa vào vector DB.

## Bước tiếp theo đề xuất

### v0.9.2

Tăng chất lượng retrieval:

- thêm golden dataset `eval/agent_golden_questions.json`;
- test thêm các câu hỏi theo từng phân khu/topic;
- thêm fallback “không có thông tin” khi retrieved context không chứa dữ kiện được hỏi.

### v1.0.0

Khi retrieval keyword/chunk đã ổn:

- thiết kế Supabase pgvector hoặc Chroma;
- tạo embedding cho `ai_knowledge_chunks.json`;
- thêm semantic search + rerank;
- thêm citation/source trong response.

## Kết luận

Version 0.9.1 đã xử lý nguyên nhân chính khiến AI trả lời sai: context RAG nghèo và không dùng đúng schema `cleaned_data`. Agent hiện đã có adapter dữ liệu mới, chunk retriever, RAG context giàu hơn và test factuality cơ bản.
