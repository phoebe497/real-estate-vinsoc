# Report MVP - Design And Architecture

## Product

**Ocean Park AI Advisor** là AI pre-sales assistant cho Vinhomes Ocean Park. MVP tập trung vào tư vấn dự án có nguồn, lead capture đúng thời điểm và CRM cho Sales/Admin.

## Architecture Source Of Truth

- File chính thức cho BTC: `ARCHITECTURE.md`
- Diagram phụ: `docs/architecture_diagram.md`
- README summary: `README.md`

## Core Architecture

- FE: Next.js 16, React 19, TypeScript, Tailwind CSS.
- BE: FastAPI, SQLAlchemy, Alembic, Pydantic Settings.
- AI: LangGraph StateGraph với `intent_node -> rag_node -> profile_node -> llm_node`.
- RAG: legacy JSON fallback và pgvector hybrid retrieval.
- DB: SQLite local, PostgreSQL production.
- Admin: JWT auth, CRM customer/conversation/sales/fallback dashboard.

## Design Decisions

- Anonymous chat first, gated lead capture second.
- `RAG_PROVIDER=legacy` default để local/demo ổn định.
- `RAG_PROVIDER=pgvector` cho standard RAG path khi có PostgreSQL/pgvector.
- Giá chốt/quỹ căn live phải handover Sales nếu không có trusted source.
- `session_id` và transcript được giữ để Sales có đủ context follow-up.
