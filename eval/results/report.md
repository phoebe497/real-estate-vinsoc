# Evaluation Report

**Date:** 2026-07-09
**System:** Ocean Park AI Advisor
**Scope:** Backend quality, LangGraph flow, RAG retrieval, deliverable readiness

## Summary

The repository now has automated evidence for code quality, RAG retrieval, pgvector-compatible ingest, LangGraph-focused tests, and a public deployment URL.

Live access:

- Public app: `https://c2-app-005.quangtm.site`
- Admin CRM: `https://c2-app-005.quangtm.site/admin/login`
- Demo admin account: `admin@gmail.com`
- Demo admin password: `admin123456789Aa@`
- Video demo: `https://drive.google.com/drive/folders/1I12vmhLrdAU4HzOzot6R_3IydwpIAieW`
- Pitch deck: `presentation/pitch_deck.html`

## Verified Commands

| Area | Command | Result |
|---|---|---|
| Python style | `python -m ruff check src tests scripts\ingest_knowledge_chunks.py scripts\verify_pgvector_retrieval.py` | PASS |
| RAG ingest smoke | `python -m pytest tests\test_scripts\test_ingest_knowledge_chunks.py -q` | PASS, `1 passed` |
| Local RAG verifier | `$env:DATABASE_URL='sqlite:///./.tmp_pytest/verify_rag.db'; $env:RAG_PROVIDER='pgvector'; $env:RAG_EMBEDDING_PROVIDER='local_hash'; python scripts\verify_pgvector_retrieval.py` | PASS, inserted 16 chunks, selected 3 chunks |
| Full backend tests | `python -m pytest tests -q` | PASS, `228 passed, 1 skipped` |
| Frontend build | `cd FE; npm.cmd run build` | PASS |

Additional stable commands for final CI sweep:

```powershell
python -m compileall src scripts
python -m pytest tests -q
```

## RAG Evidence

| Capability | Evidence | Status |
|---|---|---|
| Chunked knowledge source | `cleaned_data/ai_knowledge_chunks.json` | Ready |
| Embedding helper | `src/services/embeddings.py` | Ready |
| Vector/full-text retriever | `src/services/retrieval.py` | Ready |
| pgvector schema | `migrations/versions/20260709_05_knowledge_chunks_pgvector.py` | Ready |
| Ingest script | `scripts/ingest_knowledge_chunks.py` | Ready |
| Deterministic verifier | `scripts/verify_pgvector_retrieval.py` | Ready |
| SQLite/local fallback | verified with `local_hash` | Ready |
| Real PostgreSQL pgvector evidence | requires Postgres URL and API key | Pending team run |

## Manual Live Cases To Capture

| ID | Input | Expected | Required Evidence |
|---|---|---|---|
| RAG-01 | "Tôi có 3.5 tỷ, muốn căn 2PN cho gia đình ở Ocean Park" | Advisor answer, no premature Sales handover | FE screenshot, API response, citations |
| RAG-02 | "Ocean Park có hồ nhân tạo và tiện ích gì nổi bật?" | Project amenities answer with citations | FE screenshot, retrieved_count |
| RAG-03 | "The Zenpark có tiện ích gì nổi bật?" | Zenpark-specific context | transcript, citations |
| RAG-04 | "Giá chốt căn 2PN Zenpark hôm nay còn căn nào?" | Does not hallucinate live inventory; handover allowed | transcript, handover flag |
| RAG-05 | "Cư dân có được miễn học phí VinUni không?" | Safe insufficient-context/refusal unless cited | transcript, status |

## Current Risk

The automated layer is ready, but scoring will be stronger after the team adds:

- 5 real chat transcripts/screenshots in `docs/report_AI/RAG_CHATBOT_EVAL_EVIDENCE.md`.
- Recorded video demo and exported PDF copy of `presentation/pitch_deck.html` if BTC requires separate binary/hosted artifacts.
