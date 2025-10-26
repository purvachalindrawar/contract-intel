# eval/run_eval.py
import json
import requests
from pathlib import Path

BASE = "http://127.0.0.1:8000"

def load_qas(path):
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            yield json.loads(line)

def run():
    path = Path(__file__).parent / "qa_eval.jsonl"
    results = []
    for q in load_qas(path):
        payload = {"question": q["question"], "top_k": 3}
        r = requests.post(f"{BASE}/ask", json=payload, timeout=30)
        try:
            ans = r.json().get("answer", "")
        except Exception:
            ans = str(r.text)
        results.append({"question": q["question"], "answer": ans, "expected": q.get("answer", "")})
  
    for r in results:
        print("Q:", r["question"])
        print("A:", r["answer"])
        print("EXP:", r["expected"])
        print("---")
    print(f"Ran {len(results)} queries")

if __name__ == "__main__":
    run()
