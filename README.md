# Contract Intelligence — Prototype

A Contract Intelligence prototype that ingests PDFs, extracts text & spans, provides deterministic audits, and a RAG QA skeleton.

## Quick features implemented
- POST `/ingest` — upload PDFs, extracts page-level text & cumulative char offsets, persists in SQLite.
- POST `/extract` — structured heuristics to extract parties, effective_date, term, governing_law, payment_terms, termination, auto_renewal, confidentiality, indemnity, liability_cap, signatories (returns evidence spans).
- POST `/ask` — retrieval + optional LLM generation. Returns `answer` and `citations` in the shape `{document_id, page, start, end}`. Uses OpenAI if `OPENAI_API_KEY` is set; otherwise returns a mocked answer. Retrieval uses vector plumbing when available and naive text fallback otherwise.
- POST `/audit` — deterministic audit rules, returns findings with severity and evidence span. Optional background webhook notifier.
- GET `/ask/stream` — SSE demo stream.
- GET `/metrics` — simple counters: ingests, asks, audits, extracts.
- Dockerized lightweight image for quick demo.
- Tests and eval helpers included.

## Public sample contracts (for evaluation)
You can download public contracts to test with (do not commit copyrighted contracts):
- Example SaaS MSA: https://www.example.com/sample_msa.pdf (replace with real public links)
- Example NDA: https://www.example.com/sample_nda.pdf
- Example Terms of Service: https://www.example.com/sample_tos.pdf

(Replace example.com links with real public contract URLs you are allowed to include. I did not include copyrighted PDFs in the repo.)

## Quickstart (PowerShell)
1. Create & activate venv:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
