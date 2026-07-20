# Architecture Diagram

> Official architecture document for BTC: `ARCHITECTURE.md`. This file keeps the Mermaid diagrams as a lightweight companion.

## System Overview

```mermaid
flowchart TB
    Guest[Guest / Buyer] --> FE[Next.js 16 Frontend<br/>public site, chat widget, admin CRM]
    Admin[Admin / Sales] --> FE

    FE -->|REST / JSON| API[FastAPI Backend]
    API --> AgentRoutes[agent_routes.py<br/>chat, recommend, customer-score]
    API --> ApiRoutes[api/v1 routers<br/>catalog, customers, auth, dashboard, fallback rules]

    AgentRoutes --> Graph[LangGraph StateGraph]
    Graph --> Intent[intent_node<br/>intent, safety, profile extraction]
    Intent -->|needs project knowledge| RAG[rag_node<br/>retrieval + citations]
    Intent -->|fixed/simple intent| Profile[profile_node<br/>lead score signal]
    RAG --> Profile
    Profile --> LLM[llm_node<br/>OpenAI-compatible chat model]

    LLM --> Provider[OpenRouter / OpenAI-compatible LLM]
    RAG --> Retriever{RAG_PROVIDER}
    Retriever -->|legacy default| JsonChunks[cleaned_data/ai_knowledge_chunks.json]
    Retriever -->|pgvector demo/production| PGVector[(PostgreSQL + pgvector<br/>knowledge_chunks)]
    PGVector --> Embeddings[OpenAI/OpenRouter/local_hash embeddings]

    ApiRoutes --> DB[(SQLite local / PostgreSQL staging)]
    AgentRoutes --> DB
    API --> Logs[AI logs / LangSmith / app logs]
```

## LangGraph Agent Flow

```mermaid
flowchart LR
    START((START)) --> Intent[intent_node]
    Intent --> Decide{route}
    Decide -->|consult, zone_match, price_query| RAG[rag_node]
    Decide -->|greeting, privacy, handover, out_of_scope| Profile[profile_node]
    RAG --> Profile
    Profile --> LLM[llm_node]
    LLM --> END((END))
```

LangGraph hiện tại là custom advisory graph, không phải ReAct tool loop thuần. Mỗi node có một trách nhiệm:

- `intent_node`: phân loại intent, phát hiện prompt injection/off-topic/privacy/handover, trích xuất profile.
- `rag_node`: dựng `RetrievalQuery`, gọi retriever, pack context, trả citations/recommended zones.
- `profile_node`: cập nhật tín hiệu lead và khuyến nghị handover khi đủ ngưỡng.
- `llm_node`: sinh câu trả lời cuối cùng từ state, RAG context và citations; có fixed response cho intent không cần LLM.

## RAG Flow

```mermaid
flowchart TD
    A[cleaned_data/ai_knowledge_chunks.json] --> B[scripts/ingest_knowledge_chunks.py]
    B --> C[chunk normalization<br/>id, domain, zone, source metadata]
    C --> D[embed_documents]
    D --> E[(knowledge_chunks<br/>embedding + search_vector)]

    Q[User query] --> N[normalize_query + classify_domain]
    N --> M[extract zone/building metadata]
    M --> EQ[embed_query]
    EQ --> VS[pgvector similarity search]
    M --> FTS[PostgreSQL full-text search]
    VS --> RRF[Reciprocal Rank Fusion]
    FTS --> RRF
    RRF --> Filter[metadata filter + dedupe + freshness/domain boosts]
    Filter --> Pack[pack_context + citation tokens]
    Pack --> Answer[LLM answer with citations]

    JsonFallback[LegacyJsonRetriever] --> Filter
    RRF -->|no eligible chunks| JsonFallback
```

Default local mode is `RAG_PROVIDER=legacy`, which uses chunked JSON retrieval without embeddings. Technical/demo mode is `RAG_PROVIDER=pgvector`, which follows the standard RAG pattern: chunk, embed, store in vector DB, retrieve top-k, pack context, then call LLM.

## Data Stores

| Store | Local | Staging/Production | Purpose |
|---|---|---|---|
| App DB | SQLite `app.db` | PostgreSQL | users, customers, conversations, messages, sales/admin data |
| RAG chunks | JSON fallback | PostgreSQL `knowledge_chunks` + pgvector | retrieval context and citations |
| Static project data | `data/`, `cleaned_data/` | seeded/ingested data | catalog and knowledge source |
| Logs | local log files | AI log server / LangSmith | demo evidence and observability |

## Deployment Notes

- Local backend uses sync SQLAlchemy. If `DATABASE_URL` is accidentally set to `postgresql+asyncpg://`, `src/db/session.py` normalizes it to `postgresql+psycopg://` for sync operations.
- pgvector retrieval still uses the async SQLAlchemy path for vector/full-text search.
- For production, run Alembic migrations and set `AUTO_CREATE_TABLES=false`.
