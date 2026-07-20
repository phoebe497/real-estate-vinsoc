# AI/RAG re-architecture plan - clear answers across legacy context, embeddings and vectorDB

Ngày: 2026-07-01

## Mục tiêu

Thiết kế lại AI Advisor để câu trả lời rõ ràng và đúng nhu cầu khách mua nhà trong cả ba chế độ:

- `RAG_PROVIDER=legacy`: đọc context từ JSON/chunks local.
- `RAG_PROVIDER=pgvector`: retrieval qua PostgreSQL/pgvector.
- Hybrid/fallback: vector lỗi hoặc chưa ingest thì fallback về lexical/JSON.

Nguyên tắc chính: vectorDB chỉ là một backend retrieval. Chất lượng trả lời phải được bảo vệ bởi intent extraction, retrieval planning, context validation, answer template và business safety rules.

## Luồng mục tiêu

```text
User question
→ intent_node: hiểu intent + nhu cầu
→ rag_node: lấy context theo plan, không lấy chung chung
→ context quality gate: kiểm tra context có đủ cho loại câu hỏi không
→ answer planner/template: dựng khung trả lời
→ llm_node: LLM chỉ viết khi cần diễn đạt tự nhiên
→ safety verifier: chặn giá chốt/quỹ căn/mã căn/hallucinated zones
→ final response
```

## Quy tắc business bắt buộc

- Không nhắc tên phân khu không có trong dữ liệu.
- Không xác nhận quỹ căn còn/hết.
- Không trả giá chốt/giá hiện hành realtime.
- Giá trong data chỉ là giá tham khảo.
- Nếu hỏi bảng hàng, mã căn, đặt cọc, quỹ căn, giá chốt: chuyển Sales.
- Nếu thiếu dữ liệu: nói rõ thiếu phần nào và hỏi thêm/đề xuất Sales, không trả fallback cụt lủn.

## Output template ưu tiên

### Recommendation theo nhu cầu

```text
Với nhu cầu của anh/chị:
- Ngân sách:
- Gia đình:
- Ưu tiên:

Em sẽ ưu tiên:

1. Phân khu A
- Loại căn/giá tham khảo:
- Vì sao phù hợp:
- Cần cân nhắc:

2. Phân khu B
...

Em nghiêng về ... nếu ...
Anh/chị muốn ưu tiên nhận nhà sớm, gần trường hay tối ưu ngân sách hơn?
```

### So sánh

Dùng bảng theo tiêu chí: giá, vị trí, tiện ích, thiết kế, đối tượng phù hợp.

### Giá

Liệt kê theo loại căn nếu có source giá. Luôn ghi “giá tham khảo”.

### Hỏi thiếu thông tin

Nếu chỉ có ngân sách nhưng thiếu mục đích/số người/loại căn, AI hỏi thêm trước khi đề xuất sâu.

## Version triển khai trong code

### 0.9.6 - Deterministic advisor layer

- Sửa profile extraction cho family size.
- Bổ sung scoring theo gia đình, trường học, ngân sách, loại căn.
- Nếu RAG có `recommended_zones`, `llm_node` có thể trả deterministic recommendation rõ ràng trước khi gọi LLM.
- Chặn fallback quá mức cho câu tư vấn thường.

### 0.9.7 - Retrieval quality gate

- Không coi project overview là đủ context cho câu hỏi tư vấn chi tiết.
- Mỗi intent cần minimum context riêng.
- Bổ sung debug metadata để biết context lấy từ đâu.

### 0.9.8 - Eval dataset

- Chuyển bộ câu hỏi khách hàng thành fixture.
- Test intent/retrieval/output constraints.
- CI bắt lỗi hallucinated zones/fallback sai.

### 0.9.9 - pgvector readiness

- Kiểm tra bảng `knowledge_chunks`, `embedding`, `search_vector`.
- Ingest chunks bằng cùng embedding provider/model với runtime.
- Bật `RAG_PROVIDER=pgvector`.
- Fallback về legacy nếu vector lỗi.

