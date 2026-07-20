# Product Scope Statement - Ocean Park AI Advisor

## In Scope

- Public website cho Vinhomes Ocean Park với trang dự án/phân khu.
- Chatbot AI tư vấn tiếng Việt qua `POST /agent/chat`.
- RAG trên knowledge chunks từ `cleaned_data/ai_knowledge_chunks.json`.
- pgvector path cho demo kỹ thuật: ingest chunks, embedding, vector search, PostgreSQL full-text search, fusion, context packing, citations.
- Lead capture sau giới hạn tin nhắn hoặc khi khách muốn gặp Sales.
- CRM/admin cho customer, conversation, sales assignment, dashboard và fallback rules.
- Evaluation evidence bằng automated tests, RAG verifier và manual test matrix.

## Out Of Scope

- Giá chốt realtime và quỹ căn realtime nếu chưa có nguồn dữ liệu live từ Sales.
- Thanh toán/cọc/booking online.
- Hỗ trợ nhiều dự án ngoài Vinhomes Ocean Park trong MVP.

## Success Criteria

- Người dùng có thể truy cập live URL và hỏi thông tin dự án.
- Câu trả lời có citation khi dùng facts từ RAG.
- Chatbot không bịa giá chốt/quỹ căn live.
- Sales/Admin đăng nhập được CRM và xem lead/conversation.
- Repo có đủ 10 deliverables theo `docs/guide/chapter-09.md`.
