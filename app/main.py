# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Contract Intelligence - Prototype")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
