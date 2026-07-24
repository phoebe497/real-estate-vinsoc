# Eval Evidencies MVP - Ocean Park AI Advisor

## Automated Evidence

Latest verified commands:

```powershell
python -m ruff check src tests scripts
python -m compileall src scripts
python -m pytest tests -q
cd FE
npm.cmd run build
```

Latest result:

- Backend tests: `228 passed, 1 skipped`
- Ruff: pass
- Compileall: pass
- FE production build: pass

## RAG Evidence

- RAG source chunks: `cleaned_data/ai_knowledge_chunks.json`
- Ingest script: `scripts/ingest_knowledge_chunks.py`
- Verifier: `scripts/verify_pgvector_retrieval.py`
- Detailed report: `docs/report_AI/RAG_CHATBOT_EVAL_EVIDENCE.md`
- Summary report: `eval/results/report.md`

## Manual Evidence Targets

The live app is available at:

- Public app: `https://vsocintern.online`
- Admin CRM: `https://vsocintern.online/admin/login`
- Demo account: `admin@gmail.com`
- Demo password: `admin123456789Aa@`

Manual test cases should cover:

- Budget + 2PN family advisory.
- Project amenities and artificial lake.
- The Zenpark-specific amenities.
- Live price/inventory handover behavior.
- Insufficient-context refusal.
- Prompt injection/fake citation refusal.
