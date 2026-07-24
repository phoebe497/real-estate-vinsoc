# Final Deliverables Checklist

Target: make the repository easy to grade for Demo Day.

| # | Deliverable | Status | File / Link | Evidence | Remaining Blocker |
|---|---|---|---|---|---|
| 1 | Source code | Ready | repository root | Backend, FE, AI code on `integration/ai-fe-final` | None |
| 2 | README | Ready | `README.md` | Problem, solution, setup, APIs, RAG/LangGraph, links | Replace live links |
| 3 | Architecture diagram | Ready | `ARCHITECTURE.md`, `docs/architecture_diagram.md` | Official architecture plus Mermaid diagrams for system, LangGraph, RAG | None |
| 4 | AI logs | Partial | `.ai-log/`, LangSmith env in `.env.example` | Logging hooks and env documented | Need real LangSmith/AI-log screenshot or URL |
| 5 | Live URL | Ready | `https://vsocintern.online` | Public URL provided | None |
| 6 | Video demo | Ready | Google Drive: `https://drive.google.com/drive/folders/1I12vmhLrdAU4HzOzot6R_3IydwpIAieW` | Video folder provided | None |
| 7 | Pitch deck | Ready | `presentation/pitch_deck.html`, source outline: `presentation/pitch_deck.md` | 6-slide HTML deck for 3-minute pitch | None |
| 8 | Weekly journal | Ready | `JOURNAL.md` | Weekly progress and lessons | None |
| 9 | Worklog | Ready | `WORKLOG.md` | Dated implementation log | None |
| 10 | Evaluation evidence | Partial | `eval/results/report.md`, `docs/report_AI/RAG_CHATBOT_EVAL_EVIDENCE.md` | Automated evidence and manual case plan | Need 5 live transcripts/screenshots |

## Technical Readiness

| Check | Command | Latest Result |
|---|---|---|
| Python style | `python -m ruff check src tests scripts\ingest_knowledge_chunks.py scripts\verify_pgvector_retrieval.py` | PASS |
| RAG ingest test | `python -m pytest tests\test_scripts\test_ingest_knowledge_chunks.py -q` | PASS |
| RAG verifier | `$env:DATABASE_URL='sqlite:///./.tmp_pytest/verify_rag.db'; $env:RAG_PROVIDER='pgvector'; $env:RAG_EMBEDDING_PROVIDER='local_hash'; python scripts\verify_pgvector_retrieval.py` | PASS |
| Full backend tests | `python -m pytest tests -q` | PASS, 228 passed, 1 skipped |
| Frontend build | `cd FE; npm.cmd run build` | PASS |

## Known Notes For Reviewers

- `RAG_PROVIDER=legacy` is the default local mode for stable demos without PostgreSQL.
- `RAG_PROVIDER=pgvector` is the standard RAG path and requires Postgres with pgvector plus chunk ingestion.
- The repository now includes both the Alembic schema and ingestion script for `knowledge_chunks`.
- Public live URL: `https://vsocintern.online`.
- Admin CRM: `https://vsocintern.online/admin/login`.
- Demo admin account for BTC: `admin@gmail.com` / `admin123456789Aa@`.
- Rotate the demo admin password after judging.
