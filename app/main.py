
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from .pdf_extract import extract_pdf_pages_with_spans, join_pages_to_full_text
from .db import init_db, SessionLocal
from .models import Document
from .retriever import Retriever
from fastapi.responses import StreamingResponse
import os, shutil, uuid, time

app = FastAPI(title="Contract Intelligence - Prototype")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="no files provided")
    db = SessionLocal()
    results = []
    for uploaded in files:
        if not uploaded.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="only pdf allowed")
        tmp_path = f"/tmp/{uuid.uuid4().hex}.pdf"
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(uploaded.file, f)
        pages = extract_pdf_pages_with_spans(tmp_path)
        full_text = join_pages_to_full_text(pages)
        doc = Document(filename=uploaded.filename, full_text=full_text, pages=pages, metadata={})
        db.add(doc)
        db.commit()
        db.refresh(doc)
        results.append({"document_id": doc.id, "filename": uploaded.filename, "pages": len(pages), "chars": len(full_text)})
        os.remove(tmp_path)
    return {"ingested": results}

from pydantic import BaseModel
from typing import List

class AskRequest(BaseModel):
    question: str
    top_k: int = 3
    document_ids: List[int] = None

@app.post("/ask")
def ask(req: AskRequest):
    retriever = Retriever()
    res = retriever.query(req.question, k=req.top_k)
    indices = res["indices"][0] if res["indices"] else []
    answer = f"(mock) Answer generated using {len(indices)} retrieved chunk(s). Question: {req.question}"
    citations = [{"index": int(i)} for i in indices]
    return {"answer": answer, "citations": citations}

@app.get("/ask/stream")
def ask_stream(q: str):
    def event_stream():
        parts = [
            "Starting retrieval...",
            "Retrieving context...",
            "Formulating answer...",
            "Finalizing..."
        ]
        for p in parts:
            yield f"data: {p}\n\n"
            time.sleep(0.2)
        yield f"data: (mock) Answer: This is the streamed answer for: {q}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
