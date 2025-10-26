import os
import shutil
import tempfile
import uuid
import time
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .pdf_extract import extract_pdf_pages_with_spans, join_pages_to_full_text
from .db import init_db, SessionLocal
from .models import Document
from .retriever import Retriever
from .audit import run_audit
from .webhook import emit_event
from .extract import extract_fields

# Optional
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = bool(OPENAI_API_KEY)
if USE_OPENAI:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
    except Exception:
        USE_OPENAI = False

app = FastAPI(title="Contract Intelligence - Prototype")

METRICS = {
    "ingest_count": 0,
    "ask_count": 0,
    "audit_count": 0,
    "extract_count": 0
}

@app.on_event("startup")
def startup():
    init_db()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/metrics")
def get_metrics():
    # return a copy
    return dict(METRICS)

@app.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    """
    Ingest PDF(s): extract pages & full_text, store to DB, return document_id.
    """
    if not files:
        raise HTTPException(status_code=400, detail="no files provided")
    db = SessionLocal()
    results = []
    for uploaded in files:
        if not uploaded.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="only pdf allowed")
        tmp_file = None
        try:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            with tmp_file as f:
                shutil.copyfileobj(uploaded.file, f)
            tmp_path = tmp_file.name
            pages = extract_pdf_pages_with_spans(tmp_path)
            full_text = join_pages_to_full_text(pages)
            doc = Document(
                filename=uploaded.filename,
                full_text=full_text,
                pages=pages,
                metadata_json={}
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            results.append({"document_id": doc.id, "filename": uploaded.filename, "pages": len(pages), "chars": len(full_text)})
            METRICS["ingest_count"] += 1
        finally:
            if tmp_file is not None:
                try:
                    os.remove(tmp_file.name)
                except OSError:
                    pass
    db.close()
    return {"ingested": results}

class AskRequest(BaseModel):
    question: str
    top_k: int = 3
    document_ids: Optional[List[int]] = None

def _call_openai(prompt: str, max_tokens: int = 256) -> str:
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini" if hasattr(openai, "ChatCompletion") else "gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.0
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"(openai-error) {str(e)}"

@app.post("/ask")
def ask(req: AskRequest):
    """
    RAG-style QA endpoint.
    - Uses Retriever to get top-k snippets (structured results with doc_id/page/start/end/text)
    - Builds prompt using snippets and either calls real LLM (if available) or returns a mock answer.
    - Always returns citations in the shape: {document_id, page, start, end}
    """
    METRICS["ask_count"] += 1
    retriever = Retriever()
    res = retriever.query(req.question, k=req.top_k)
    results = res.get("results", [])

    snippets_text = []
    citations = []
    for i, r in enumerate(results):
        citations.append({
            "document_id": r["document_id"],
            "page": r.get("page"),
            "start": r["start"],
            "end": r["end"]
        })
        snippets_text.append(f"[{i+1}] (doc:{r['document_id']} page:{r.get('page')}) {r['text']}")

    if USE_OPENAI and snippets_text:
        prompt = (
            "You are a contract assistant. Answer the question using ONLY the evidence below. "
            "If the evidence does not contain the answer, say 'I don't know'.\n\n"
            f"Question: {req.question}\n\n"
            "Evidence:\n" + "\n\n".join(snippets_text) + "\n\n"
            "Answer concisely and include citations like (doc:page:start-end) where appropriate."
        )
        answer_text = _call_openai(prompt)
    else:
        answer_text = f"(mock) Answer generated using {len(snippets_text)} snippet(s). Question: {req.question}"

    return {"answer": answer_text, "citations": citations}

@app.get("/ask/stream")
def ask_stream(q: str):
    def event_stream():
        parts = ["Starting retrieval...", "Retrieving context...", "Formulating answer...", "Finalizing..."]
        for p in parts:
            yield f"data: {p}\n\n"
            time.sleep(0.2)
        yield f"data: (mock) Answer: This is the streamed answer for: {q}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

class AuditRequest(BaseModel):
    document_id: int

@app.post("/audit")
def audit(req: AuditRequest, background_tasks: BackgroundTasks, webhook_url: Optional[str] = None):
    METRICS["audit_count"] += 1
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    db.close()
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    findings = run_audit(doc.full_text)
    if webhook_url:
        payload = {"document_id": req.document_id, "findings_count": len(findings), "sample_findings": findings[:3]}
        background_tasks.add_task(emit_event, webhook_url, payload)
    return {"findings": findings}

@app.post("/extract")
def extract_document(document_id: int):
    """
    Return structured extraction for given document id.
    """
    METRICS["extract_count"] += 1
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == document_id).first()
    db.close()
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    fields = extract_fields(doc.full_text)
    return {"document_id": document_id, "extraction": fields}

@app.post("/webhook/events")
def webhook_receiver(payload: dict):
    print("WEBHOOK RECEIVED:", payload)
    return {"status": "received"}
