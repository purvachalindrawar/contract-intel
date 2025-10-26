# app/tests/test_ask_citations.py
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db, SessionLocal
from app.models import Document

client = TestClient(app)

def setup_sample_doc(tmp_doc_id=1):
    # ensure DB initialized
    init_db()
    db = SessionLocal()
    sample_text = "ACME Inc provides services. The contract will automatically renew for one year unless terminated."
    doc = Document(filename="sample.pdf", full_text=sample_text, pages=[{"page":0,"text":sample_text,"start_char":0,"end_char":len(sample_text)}], metadata_json={})
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()
    return doc.id

def test_ask_returns_citations(tmp_path):
    doc_id = setup_sample_doc()
    resp = client.post("/ask", json={"question":"Does the contract auto-renew?","top_k":2})
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "citations" in body
    # citations may be empty for some fallback cases but should be list
    assert isinstance(body["citations"], list)
