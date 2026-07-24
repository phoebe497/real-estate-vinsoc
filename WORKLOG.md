# Worklog - Team 005

## 2026-06-08

| Member | Task | Status | Output | Time |
|---|---|---|---|---|
| YenPhuong | Xác định bài toán AI advisor, scope RAG và các nhóm câu hỏi cần hỗ trợ | Done | Problem framing, RAG topics, lead flow draft | 3h |
| YenPhuong + MinhQuang | Crawl và phân loại data thô theo phân khu, tiện ích, loại căn, giá tham khảo | Done | Raw data và mapping topic ban đầu | 5h |
| MinhQuang | Dựng skeleton BE FastAPI, cấu hình settings và health check | Done | `src/main.py`, `src/config.py` | 4h |
| MinhQuang | Dựng nền FE Next.js và layout public cho dự án | Done | `FE/` app structure | 4h |

**Tổng kết ngày:** Team chốt hướng sản phẩm **Ocean Park AI Advisor**, có data ban đầu và nền FE/BE để bắt đầu tích hợp.

## 2026-06-15

| Member | Task | Status | Output | Time |
|---|---|---|---|---|
| YenPhuong | Thiết kế LangGraph state và các node `intent_node`, `rag_node`, `profile_node`, `llm_node` | Done | `src/agents/` | 5h |
| YenPhuong | Viết prompt/guardrail cho intent, privacy, out-of-scope và handover | Done | Intent handling và fixed responses | 3h |
| MinhQuang | Implement API chat, customer capture và lưu conversation/message | Done | `/agent/chat`, `/api/v1/customers/capture` | 5h |
| MinhQuang | Tích hợp chat widget FE với backend agent API | Done | Chat widget gọi được BE | 4h |

**Tổng kết ngày:** Luồng chat AI hoạt động được từ FE sang BE, có `session_id`, lưu hội thoại và bắt đầu hỗ trợ lead capture.

## 2026-06-22

| Member | Task | Status | Output | Time |
|---|---|---|---|---|
| YenPhuong | Chuẩn hóa knowledge chunks và xây retrieval flow cho RAG local | Done | `cleaned_data/ai_knowledge_chunks.json`, `LegacyJsonRetriever` | 5h |
| YenPhuong | Thêm citations, context packing, metadata boost và fallback cho retrieval | Done | `src/services/retrieval.py` | 5h |
| MinhQuang | Hoàn thiện CRM/admin APIs, sales assignment và dashboard stats | Done | `src/api/`, `src/models/` | 5h |
| MinhQuang | Bổ sung FE admin screens cho customer, sales và fallback rules | Done | `FE/src/app/admin/` | 4h |

**Tổng kết ngày:** RAG có thể trả lời từ chunks với citation; CRM/admin đủ luồng cơ bản để Sales xem và xử lý lead.

## 2026-06-29

| Member | Task | Status | Output | Time |
|---|---|---|---|---|
| YenPhuong | Thêm regression tests cho RAG, handover sớm và `insufficient_context` | Done | `tests/test_agents/` | 4h |
| YenPhuong | Thiết kế path pgvector: embedding, vector search, full-text search, fusion | Done | `PgVectorHybridRetriever` | 4h |
| MinhQuang | Fix integration FE/BE, validation và các route cần cho demo | Done | FE + BE integration fixes | 5h |
| MinhQuang | Chạy kiểm thử API/E2E và rà lại flow lead capture | Done | API/E2E test evidence | 3h |

**Tổng kết ngày:** Core flow ổn định hơn, có regression tests bảo vệ các lỗi quan trọng trong advisor và lead handoff.

## 2026-07-08

| Member | Task | Status | Output | Time |
|---|---|---|---|---|
| YenPhuong | Thêm migration `knowledge_chunks`, ingest script và verifier `local_hash` cho pgvector RAG | Done | Migration, ingest, verifier, pytest smoke | 5h |
| YenPhuong | Cập nhật evaluation report và manual RAG evidence matrix | Done | `eval/results/report.md`, `docs/report_AI/RAG_CHATBOT_EVAL_EVIDENCE.md` | 3h |
| MinhQuang | Hoàn thiện README, architecture diagram, deliverables checklist, pitch/video docs | Done | README, docs, presentation source | 5h |
| MinhQuang | Chạy quality gates cuối: Ruff, compileall, pytest, FE build | Done | 228 passed, FE build pass | 3h |

**Tổng kết ngày:** Bộ deliverables đã sẵn sàng ở mức repo, live URL hiện tại là `https://vsocintern.online`; phần còn lại trước khi nộp là video demo, pitch deck export và 5 transcript/screenshot live.
