# app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from .pdf_extract import extract_pdf_pages_with_spans, join_pages_to_full_text
from .db import init_db, SessionLocal
from .models import Document
import os, shutil, uuid, tempfile

app = FastAPI(title="Contract Intelligence - Prototype")

@app.on_event("startup")
def startup():
    # initialize DB (creates tables if not present)
    init_db()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    """
    Accept one or more PDF files. Uses tempfile.NamedTemporaryFile to be cross-platform.
    Persists documents to DB (Document.model) and returns document ids and stats.
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
            # Create a cross-platform temporary file
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            with tmp_file as f:
                shutil.copyfileobj(uploaded.file, f)
            tmp_path = tmp_file.name

            # Extract pages & text
            pages = extract_pdf_pages_with_spans(tmp_path)
            full_text = join_pages_to_full_text(pages)

            # Persist document to DB
            doc = Document(
                filename=uploaded.filename,
                full_text=full_text,
                pages=pages,
                metadata_json={}   # use metadata_json (avoid reserved name)
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            results.append({
                "document_id": doc.id,
                "filename": uploaded.filename,
                "pages": len(pages),
                "chars": len(full_text)
            })
        finally:
            # Always try to remove the temp file
            if tmp_file is not None:
                try:
                    os.remove(tmp_file.name)
                except OSError:
                    pass

    return {"ingested": results}
