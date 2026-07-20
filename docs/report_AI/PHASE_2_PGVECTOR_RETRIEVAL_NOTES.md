# Phase 2: Ghi Chú Hybrid Retrieval Với pgvector

## Rollout flag

Dùng `RAG_PROVIDER=legacy` cho retriever hiện tại dựa trên JSON.
Dùng `RAG_PROVIDER=pgvector` sau khi schema Supabase/PostgreSQL và embeddings đã sẵn sàng.

Rollback chỉ cần đổi cấu hình:

```env
RAG_PROVIDER=legacy
```

## Migration Supabase Đề Xuất

Ứng dụng vẫn giữ unit tests độc lập với live Supabase. Trước khi bật `RAG_PROVIDER=pgvector`, hãy apply SQL dưới đây trên Supabase hoặc đưa vào Alembic migration.

```sql
create extension if not exists vector;

alter table knowledge_chunks
  add column if not exists document_id text,
  add column if not exists title text,
  add column if not exists project_slug text,
  add column if not exists zone_slug text,
  add column if not exists subzone_slug text,
  add column if not exists building_code text,
  add column if not exists domain text,
  add column if not exists source_url text,
  add column if not exists source_type text default 'knowledge_chunk',
  add column if not exists confidence_level text default 'medium',
  add column if not exists data_period text,
  add column if not exists effective_from timestamptz,
  add column if not exists effective_to timestamptz,
  add column if not exists is_active boolean default true,
  add column if not exists extra_metadata jsonb,
  add column if not exists embedding vector(1536),
  add column if not exists search_vector tsvector;

update knowledge_chunks
set search_vector = to_tsvector(
  'simple',
  coalesce(title, '') || ' ' ||
  coalesce(topic, '') || ' ' ||
  coalesce(subdivision_name, '') || ' ' ||
  coalesce(content, '')
)
where search_vector is null;

create index if not exists idx_knowledge_chunks_embedding
  on knowledge_chunks using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists idx_knowledge_chunks_search_vector
  on knowledge_chunks using gin (search_vector);

create index if not exists idx_knowledge_chunks_domain
  on knowledge_chunks (domain);

create index if not exists idx_knowledge_chunks_zone_slug
  on knowledge_chunks (zone_slug);

create index if not exists idx_knowledge_chunks_active
  on knowledge_chunks (is_active);
```

## Yêu Cầu Ingestion

Mỗi chunk nên có các trường sau:

- `chunk_id`
- `document_id`
- `title`
- `content`
- `source_url`
- `source_type`
- `domain`
- `confidence_level`
- `data_period`
- canonical metadata: `project_slug`, `zone_slug`, `subzone_slug`, `building_code` nếu có
- `embedding`
- `search_vector`

Backend validate citation URLs từ trusted chunk metadata. LLM chỉ nhìn thấy citation token dạng `[C1]`, `[C2]` và không được tự tạo URL trực tiếp.

## Script Ingestion Trong Repository

Dry-run normalized chunks mà không gọi network hoặc database:

```powershell
python scripts\ingest_knowledge_chunks.py --dry-run
```

Apply schema và ingest vào PostgreSQL/Supabase database đang được cấu hình:

```powershell
python scripts\ingest_knowledge_chunks.py --migrate --apply
```

Để semantic retrieval đạt chất lượng production, dùng `RAG_EMBEDDING_PROVIDER=openrouter` cùng `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` và `OPENROUTER_MODEL=openai/text-embedding-3-small`. Provider `openai` vẫn được giữ cho các endpoint embedding OpenAI-compatible trực tiếp. Provider `local_hash` deterministic và hữu ích cho bootstrap/tests, nhưng **không phải semantic embedding model**.

Chat provider và embedding provider có thể cấu hình tách biệt:

```env
OPENAI_BASE_URL=https://api.freemodel.dev/v1
OPENAI_MODEL=gpt-4o-mini

OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openai/text-embedding-3-small
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
RAG_EMBEDDING_PROVIDER=openrouter
```
