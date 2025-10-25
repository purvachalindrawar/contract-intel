# app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from .pdf_extract import extract_pdf_pages_with_spans, join_pages_to_full_text
import os, shutil, uuid, tempfile  # <-- added tempfile

app = FastAPI(title="Contract Intelligence - Prototype")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    """
    Accept one or more PDF files. For each:
      - write to a temp file (cross-platform)
      - extract pages with spans
      - return filenames + counts
    """
    if not files:
        raise HTTPException(status_code=400, detail="no files provided")

    results = []
    for uploaded in files:
        if not uploaded.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="only pdf allowed")

        tmp_dir = tempfile.gettempdir()
        tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.pdf")

        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(uploaded.file, f)

        pages = extract_pdf_pages_with_spans(tmp_path)
        full_text = join_pages_to_full_text(pages)
        results.append({
            "filename": uploaded.filename,
            "pages": len(pages),
            "chars": len(full_text)
        })

       
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return {"ingested": results}
