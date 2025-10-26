# 🧠 Contract Intelligence — Backend Take-Home Assignment

### Submitted by: **Purva Chalindrawar**  

---

## 🚀 Overview

**Contract Intelligence** is a backend service that automates the ingestion, extraction, and analysis of contract PDFs.  
It provides endpoints for:

- Uploading and parsing PDFs (`/ingest`)
- Extracting structured contract fields (`/extract`)
- Asking contextual questions (`/ask`, `/ask/stream`)
- Running deterministic risk audits (`/audit`)
- Reporting metrics and webhook updates (`/metrics`, `/webhook/events`)

This project is implemented entirely in **Python (FastAPI + SQLAlchemy)**,  
and containerized using **Docker** and **docker-compose** for easy deployment.

---

## ⚙️ Setup & Run Locally

### Clone the Repository
```bash
git clone https://github.com/[your_repo_link_here].git
cd contract-intel
```


### (Option A) Local Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


### (Option B) Run with Docker
```bash
docker-compose -f docker/docker-compose.yml up --build

## 🧠 API Endpoints Summary

Below is the complete list of implemented API endpoints in this project.

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/healthz` | **GET** | Returns a simple health check (`{"status": "ok"}`) to verify the API is running. |
| `/ingest` | **POST** | Upload one or multiple PDF files. Extracts text, stores metadata, and returns generated `document_id`s. |
| `/extract` | **POST** | Given a `document_id`, extracts key contract fields such as parties, effective date, term, governing law, payment terms, termination, auto-renewal, confidentiality, indemnity, and liability cap. |
| `/ask` | **POST** | Accepts a question and performs document retrieval (RAG). Returns a mock LLM-based answer with citations (document ID + page range). |
| `/ask/stream` | **GET** | Provides a mock Server-Sent Events (SSE) stream version of the `/ask` endpoint for streaming responses. |
| `/audit` | **POST** | Runs deterministic rule-based audits on the uploaded document(s). Detects risky clauses like unlimited liability, auto-renewal, or broad indemnity. Returns findings with severity and evidence. |
| `/metrics` | **GET** | Returns usage metrics such as total documents ingested, audits performed, and questions asked. |
| `/webhook/events` | **POST** | Accepts webhook event notifications (used for background audit completion events). |
| `/docs` | **GET** | Automatically generated Swagger UI documentation for all endpoints. |

---

### 🔍 Example PowerShell Commands

**Health Check**
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/healthz' -Method GET

**Upload a PDF**
```powershell
curl.exe -X POST "http://127.0.0.1:8000/ingest" -F "files=@sample.pdf"

**Extract Structured Data**
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/extract?document_id=1' -Method POST

**Ask a Question**
```powershell   
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/ask' -Method POST -ContentType 'application/json' -Body '{ "question": "What is the termination period?", "top_k": 2 }'

**Run an Audit**
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/audit' -Method POST -ContentType 'application/json' -Body '{ "document_id": 1 }'

**Check Metrics**
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/metrics' -Method GET

## 🔍 Features Implemented

Below is a complete list of all major features and components implemented in this project.

### 🧩 Core Functionalities
- **PDF Ingestion (`/ingest`)** – Upload and parse single or multiple PDFs. Extracts page-level text and stores metadata (filename, pages, character counts) in a SQLite database.
- **Contract Field Extraction (`/extract`)** – Extracts structured information such as:
  - Parties involved  
  - Effective date  
  - Term and renewal conditions  
  - Governing law and jurisdiction  
  - Payment and liability clauses  
  - Confidentiality and indemnity  
  - Signatories and key terms
- **Question Answering (`/ask`)** – Allows users to ask contextual questions about uploaded documents using a Retrieval-Augmented Generation (RAG) pipeline.  
  - Includes **mock LLM response** for offline portability.  
  - Returns both the answer and **citations** to specific document segments.
- **Audit Engine (`/audit`)** – Runs deterministic, rule-based risk detection on documents.  
  - Detects risky clauses such as:
    - Auto-renewal without notice
    - Unlimited liability exposure
    - Broad indemnity coverage  
  - Returns structured findings with evidence text and severity labels.
- **Webhook Integration (`/webhook/events`)** – Sends asynchronous background notifications upon audit completion to a provided webhook URL.
- **Metrics (`/metrics`)** – Tracks total documents ingested, audits performed, and questions asked since server startup.
- **Streaming (`/ask/stream`)** – Demonstrates a mock SSE endpoint that streams partial responses, mimicking real-time LLM output.
- **Health Check (`/healthz`)** – Provides a lightweight service status endpoint.
- **Interactive Docs (`/docs`)** – Auto-generated Swagger UI powered by FastAPI for testing and documentation.

---

### 🧠 System Design Features
- **Database Layer** – Implemented using **SQLAlchemy ORM** with automatic schema creation via `Base.metadata.create_all()`.  
  - Uses **SQLite** for local development (replaceable with Postgres in production).  
- **PDF Parser** – Built on **PyMuPDF**, providing accurate page-level text extraction and character offset mapping.
- **Embedding & Retrieval Layer** –  
  - Modular `EmbeddingProvider` with mock and real implementations.  
  - `Retriever` supports top-k search using vector embeddings or mock fallbacks when FAISS is unavailable.
- **Audit Rules Engine** – Implemented using **regex-based deterministic rules** for explainable and consistent clause detection.
- **Background Tasks** – FastAPI’s `BackgroundTasks` used to send webhook events asynchronously without blocking API response.
- **Metrics System** – Simple in-memory counter-based metrics with JSON output for easy observability.
- **Testing Suite** – Basic **pytest** tests to validate `/healthz`, `/audit`, and key endpoint behaviors.
- **Containerization** – Complete **Dockerfile** and **docker-compose** configuration for reproducible environments and easy demo setup.

---

### 🧰 Developer Experience
- Clear **README** with setup, usage, and architecture details.
- Incremental **commit history** showing logical development progression.
- **Prompts**, **eval**, and **design_doc.md** directories added to align with take-home assignment requirements.
- Mock LLM implementation ensures **no API keys** or **external dependencies** are required for demo execution.

---

✅ **All features listed in the Senior Backend Engineer assignment document are implemented and verified.**  
🧠 **The system demonstrates ingestion, extraction, retrieval, auditing, metrics, and background tasks end-to-end.**
