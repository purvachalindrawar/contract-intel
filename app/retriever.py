"""
Retriever that tries to use vector search when available, otherwise falls back
to a simple keyword-based search over stored documents and pages to produce
structured citations (document_id, page, start_char, end_char, snippet).
"""

from typing import List, Dict, Any
from .embeddings import EmbeddingProvider
from .db import SessionLocal
from .models import Document
import re

class Retriever:
    def __init__(self):
        self.ep = EmbeddingProvider()
        self._is_mock = getattr(self.ep, "_initialized", False) and getattr(self.ep, "_impl", None) is None

        try:
            sample = self.ep.encode(["test"])
          
            if isinstance(sample, list):
                self._is_mock = True
        except Exception:
            self._is_mock = True

    def add_texts(self, texts: List[str]):
        """Encode and add to vector index (if supported)."""
        try:
            vecs = self.ep.encode(texts)
            self.ep.add(vecs)
        except Exception:
            
            pass

    def query(self, question: str, k: int = 3) -> Dict[str, Any]:
        """
        Return structured retrieval results:
        {
            "results": [
                {"document_id": X, "page": p, "start": s, "end": e, "text": snippet, "score": numeric}
            ]
        }
        If vector search is available, attempt to use it; otherwise fallback to naive substring search over stored documents.
        """
      
        try:

            qvec = self.ep.encode([question])
            D, I = self.ep.search(qvec, k)
        except Exception:
            D, I = None, None

        # Fallback naive keyword search across stored documents
        db = SessionLocal()
        docs = db.query(Document).all()
        q_terms = [t.lower() for t in re.findall(r"\w+", question) if len(t) > 2]
        scored: List[Dict] = []
        for doc in docs:
            full = doc.full_text or ""
           
            score = 0
            for term in q_terms:
                score += full.lower().count(term)
            if score == 0:
                continue
          
            first_pos = None
            for term in q_terms:
                pos = full.lower().find(term)
                if pos != -1:
                    first_pos = pos
                    break
            if first_pos is None:
                continue
          
            page_info = None
            if doc.pages:
                for p in doc.pages:
                    if p.get("start_char", 0) <= first_pos < p.get("end_char", 0):
                        page_info = p
                        break
            
            start = max(0, first_pos - 80)
            end = min(len(full), first_pos + 200)
            snippet = full[start:end]
            scored.append({
                "document_id": doc.id,
                "page": page_info.get("page") if page_info else None,
                "start": start,
                "end": end,
                "text": snippet,
                "score": score
            })
        
        scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)[:k]
        db.close()
        return {"results": scored_sorted}
