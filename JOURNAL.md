# Weekly Journal - Team C2-App-005

## Week 1: 2026-06-08 - 2026-06-14

### Mục tiêu

- Xác định bài toán cho **Ocean Park AI Advisor**: hỗ trợ khách tìm hiểu Vinhomes Ocean Park và giúp Sales nhận lead có ngữ cảnh.
- Crawl data ban đầu từ các trang dự án, phân khu, căn hộ, tiện ích và thông tin liên quan.
- Chuẩn hóa data để có thể dùng cho FE, BE và RAG sau này.
- Dựng định hướng kiến trúc FE/BE tối thiểu cho sản phẩm demo.

### Đã hoàn thành

- Thu thập dữ liệu thô về Vinhomes Ocean Park, phân khu, tiện ích, loại căn và một số thông tin giá tham khảo.
- Làm sạch data thành các file seed/cleaned data để backend có thể đọc ổn định.
- Xác định user flow chính: khách xem thông tin dự án, chat với AI advisor, để lại thông tin khi có nhu cầu, Sales xem lại transcript trong CRM.
- Dựng nền tảng BE bằng FastAPI, cấu hình settings, health check và cấu trúc service/API.
- Dựng nền tảng FE bằng Next.js để hiển thị giao diện public và chuẩn bị vị trí tích hợp chat widget.

### Khó khăn và cách xử lý

| Khó khăn | Cách xử lý | Kết quả |
|---|---|---|
| Data bất động sản nằm rải rác và không đồng nhất cách gọi phân khu/loại căn | Chuẩn hóa slug, tên phân khu, topic và source metadata | Có nền data đủ dùng cho catalog và RAG |
| Thông tin giá/quỹ căn dễ stale | Chỉ xem giá là tham khảo, định hướng AI không được bịa giá chốt hoặc quỹ căn live | Giảm rủi ro hallucination |
| Chưa rõ nên ưu tiên FAQ hay tư vấn bán hàng | Chốt hướng pre-sales advisor có lead capture và CRM | Sản phẩm có business flow rõ hơn |

### Bài học

- Data quality quyết định chất lượng RAG nhiều hơn prompt đơn lẻ.
- FE và BE cần thống nhất sớm về API shape để tránh chỉnh lại nhiều khi tích hợp.
- Với bất động sản, citation và wording an toàn quan trọng ngang với độ mượt của câu trả lời.

## Week 2: 2026-06-15 - 2026-06-21

### Mục tiêu

- Xây dựng chatbot AI theo hướng advisor, không chỉ là FAQ bot.
- Tích hợp LangGraph để tách intent, RAG, profile và LLM response.
- Bắt đầu luồng lead capture và lưu conversation.

### Đã hoàn thành

- Implement `POST /agent/chat` với LangGraph gồm `intent_node`, `rag_node`, `profile_node`, `llm_node`.
- Thêm logic nhận diện nhu cầu như budget, unit type, purpose, timeline và tín hiệu muốn gặp Sales.
- Tạo flow anonymous chat trước, sau đó yêu cầu contact khi vượt giới hạn hoặc có tín hiệu handover.
- BE lưu customer, conversation, message và metadata cần thiết cho CRM.
- FE tích hợp chat widget với backend agent API.

### Khó khăn và cách xử lý

| Khó khăn | Cách xử lý | Kết quả |
|---|---|---|
| AI có thể chuyển Sales quá sớm | Tách intent/handover thành logic riêng và thêm điều kiện ngữ cảnh | Advisor flow tự nhiên hơn |
| Cần giữ transcript cho Sales | Dùng `session_id` và lưu message history | Sales có đủ ngữ cảnh follow-up |
| Một số câu hỏi không cần LLM | Dùng fixed response/fallback cho greeting, privacy, out-of-scope | Giảm chi phí token và tăng ổn định |

### Bài học

- LangGraph giúp luồng AI dễ debug hơn vì mỗi node có trách nhiệm rõ.
- Lead capture nên xuất hiện đúng thời điểm, nếu quá sớm sẽ làm giảm trải nghiệm tư vấn.

## Week 3: 2026-06-22 - 2026-06-28

### Mục tiêu

- Cải thiện RAG để trả lời có căn cứ và giảm hallucination.
- Thêm citations, context packing và fallback khi retrieval không đủ tốt.
- Bổ sung test cho các case lỗi phát hiện trong quá trình tích hợp.

### Đã hoàn thành

- Chuẩn hóa `cleaned_data/ai_knowledge_chunks.json` thành nguồn chunk chính cho RAG local.
- Implement `LegacyJsonRetriever` cho chế độ local ổn định và `PgVectorHybridRetriever` cho pgvector.
- Kết hợp vector search, PostgreSQL full-text search, Reciprocal Rank Fusion, metadata boost và fallback.
- Thêm citations vào response để người dùng thấy nguồn thông tin.
- Viết regression tests cho lỗi handover sớm và lỗi trả `insufficient_context` dù data amenities có tồn tại.

### Khó khăn và cách xử lý

| Khó khăn | Cách xử lý | Kết quả |
|---|---|---|
| pgvector cần embedding cùng provider/model/dimension | Ghi rõ quy tắc ingest/query và thêm `local_hash` cho smoke test | Có đường test không cần API key |
| Retrieval có thể fail nếu chưa ingest DB | Giữ `legacy` fallback bằng JSON chunks | Local demo ổn định hơn |
| Citation cần khớp context thật | Pack context kèm citation token và metadata | Giảm nguy cơ citation giả |

### Bài học

- RAG tốt cần cả retrieval, reranking/fusion, metadata filter và fallback, không chỉ cần embedding.
- Smoke test bằng `local_hash` hữu ích để kiểm tra pipeline mà không tốn token/API key.

## Week 4: 2026-06-29 - 2026-07-08

### Mục tiêu

- Hoàn thiện deliverables cho Demo Day.
- Đồng bộ README, architecture diagram, evaluation evidence, Journal và Worklog.
- Chuẩn hóa tên sản phẩm **Ocean Park AI Advisor**.

### Đã hoàn thành

- Cập nhật README theo boilerplate của chương trình và giữ bản integration notes riêng.
- Hoàn thiện architecture diagram mô tả Next.js FE, FastAPI BE, LangGraph, RAG legacy/pgvector và CRM.
- Thêm migration `knowledge_chunks`, script ingest và verifier cho pgvector RAG.
- Cập nhật evaluation report, checklist deliverables, video demo plan và pitch deck source.
- Chạy kiểm tra chất lượng: Ruff, compileall, pytest và FE build.

### Khó khăn và cách xử lý

| Khó khăn | Cách xử lý | Kết quả |
|---|---|---|
| Deliverables nằm rải rác nhiều file | Tạo checklist cuối cùng và link đến từng artifact | Reviewer dễ kiểm tra hơn |
| Cần cung cấp link thật cho BTC chấm | Cập nhật live URL `https://c2-app-005.quangtm.site` và admin URL `/admin/login` vào tài liệu | Reviewer có thể truy cập sản phẩm trực tiếp |
| README cũ chứa nhiều ghi chú integration quan trọng | Đổi sang `README_integration.md` thay vì xóa | Không mất context kỹ thuật |

### Bài học

- Demo Day cần cả sản phẩm chạy được và bằng chứng kiểm thử rõ ràng.
- Tài liệu tốt phải nói đúng trạng thái thật: phần nào ready, phần nào còn cần team bổ sung link/live evidence.
