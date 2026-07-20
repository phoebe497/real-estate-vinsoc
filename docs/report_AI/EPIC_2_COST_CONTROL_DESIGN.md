# Epic 2: Cost Control Design

## 1. Cost Control Strategy & Constraints

### Architectural Decision Record (ADR): SQLite for Quota & History
**Status:** Accepted
**Context:** We need to enforce a rate limit (5 req/min) and daily quota (100 req/day) to avoid Token Budget exhaustion. Furthermore, context must be maintained to provide seamless Chat History. 
**Decision:** We implemented an SQLite database via SQLAlchemy ORM to track `conversations` and `messages`. Rate limiting is enforced at the route level via SQL counting queries (checking usage over time ranges).
- For production scalability, this schema is entirely compatible with PostgreSQL.
- **Polite 429 Handling:** Instead of hard HTTP 429 status codes, the server returns an HTTP 200 with a polite "too many requests" message to keep user interaction smooth without showing technical errors.

## 2. Database Schema (SQLite / PostgreSQL Compatible)

### `conversations` Table
Tracks session lifecycles and quotas.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `VARCHAR(36)` | Primary Key | UUID identifying the conversation thread |
| `session_id` | `VARCHAR(100)` | Unique, Indexed | Client-side tracking ID (Cookie/Header) |
| `last_intent` | `VARCHAR(50)` | Nullable | Most recent detected intent |
| `daily_usage_count` | `INTEGER` | Default 0 | Counts requests to enforce max 100/day |
| `created_at` | `DATETIME` | Default NOW() | Creation timestamp |
| `updated_at` | `DATETIME` | Default NOW() | Updated on each message to track activity |

### `messages` Table
Tracks Chat History.

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `VARCHAR(36)` | Primary Key | UUID for the message |
| `conversation_id` | `VARCHAR(36)` | Foreign Key, Indexed | Reference to `conversations.id` |
| `role` | `VARCHAR(20)` | Not Null | `"user"`, `"assistant"`, or `"system"` |
| `content` | `TEXT` | Not Null | Message payload |
| `created_at` | `DATETIME` | Default NOW() | Creation timestamp |

## 3. Token Budget Strategy

- **Prompt Truncation:** We strictly load only the last $N$ messages from the `messages` table for LangGraph context injection to cap the context window (e.g., $N=10$).
- **Retrieval Augmented Generation (RAG):** Context chunks are strictly bounded.
- **Hard Quotas:** 
    - *Spike Protection:* 5 requests per minute per `session_id`.
    - *Budget Protection:* 100 requests per 24 hours per `session_id`.

## 4. Future Redis Design (For Distributed Scale)

While currently using SQLite, moving to a distributed environment (e.g., multiple FastAPI workers) requires Redis for Atomic Rate Limiting:
- **Key Format:** `rate_limit:min:{session_id}` and `rate_limit:day:{session_id}`
- **Data Structure:** Sliding Window Log or simple Token Bucket (using Redis `INCR` and `EXPIRE`).
- **Advantage:** O(1) in-memory checks bypassing disk I/O, preventing race conditions under high concurrent load.

## 5. Metrics to Track

1. `rate_limit_hits_total`: Count of sessions hitting the 5 req/min limit.
2. `quota_exhausted_total`: Count of sessions hitting the 100 req/day limit.
3. `average_tokens_per_session`: Track total LLM tokens used per conversation to map directly to cost.
