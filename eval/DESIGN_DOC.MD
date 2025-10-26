# Contract Intelligence — Design Document (short)

## Purpose
This prototype ingests PDF contracts, extracts page-level text with character offsets, persists documents, runs deterministic audits for risky clauses, and provides a RAG-style QA skeleton. The goal is an explainable, pluggable backend that can integrate local or remote LLMs.

## Architecture (components)
- **API (FastAPI)** - endpoints for ingest, extract, ask, audit and metrics.
- **PDF parsing (PyMuPDF)** - extracts page text and cumulative character offsets.
- **Persistence (SQLAlchemy + SQLite)** - stores Document rows with `full_text` and page metadata (page number, start/end char).
- **Retriever (pluggable)** - `EmbeddingProvider` for real embeddings + FAISS; fallback naive text search for environments without heavy libs.
- **LLM integration (pluggable)** - mock by default; optional OpenAI integration if `OPENAI_API_KEY` is provided.
- **Audit engine** - deterministic, regex-based rules returning precise spans and evidence snippets.
- **Webhook emitter** - background notification on long tasks (audit) for event-driven workflows.

## Data model
- `Document` table: `id`, `filename`, `uploaded_at`, `metadata_json`, `full_text`, `pages` (JSON list of page dicts with `page`, `text`, `start_char`, `end_char`).

## Evidence mapping & citations
- Page-level cumulative char offsets are stored for precise citations.
- `/ask` returns citations shaped as `{document_id, page, start, end}` that map uniquely to snippet positions in `full_text`.

## Chunking & retrieval rationale
- For small datasets (few documents), deterministic full-text fallback works reliably and preserves exact offsets for citations.
- For larger datasets, embeddings + FAISS are recommended: chunk documents by sentence windows or by page; store mapping from vector index to document/page/offset to produce precise citations.
- This prototype uses a hybrid approach: vector plumbing is implemented, but to keep Docker small we provide a naive fallback that always produces correct span-based citations.

## Security & privacy
- Do not commit API keys; use `.env` and `.env.example`.
- For production, use an authenticated upload endpoint, per-tenant separation, and encrypt document storage.
- Webhooks should be signed (HMAC) and use HTTPS.

## Limitations & next steps
- The extraction heuristics are simple regex-based; LLM-based structured extraction would be more accurate for varied contract language.
- Add database migrations (Alembic) for production schema evolution.
- Add per-document chunk-to-vector mapping to enable exact vector-citation mapping with FAISS.
- Add user authentication, audit logs, and rate limiting.

