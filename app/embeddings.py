"""
Lightweight, resilient embedding provider wrapper.

Behavior:
- If heavy libs (numpy, sentence-transformers, faiss) are available,
  use them lazily.
- If they are NOT available (e.g., in lightweight Docker), we provide
  a MockEmbeddingProvider that returns safe placeholders and does NOT crash.
This allows the app to run ingestion/audit endpoints in lightweight containers.
"""

import os
from typing import List, Dict
_HAS_NUMPY = False
_HAS_SENT_TRANS = False
_HAS_FAISS = False

def _try_imports():
    global _HAS_NUMPY, _HAS_SENT_TRANS, _HAS_FAISS
    try:
        import numpy as np  
        _HAS_NUMPY = True
    except Exception:
        _HAS_NUMPY = False
    try:
        from sentence_transformers import SentenceTransformer  
        _HAS_SENT_TRANS = True
    except Exception:
        _HAS_SENT_TRANS = False
    try:
        import faiss  
        _HAS_FAISS = True
    except Exception:
        _HAS_FAISS = False
class MockEmbeddingProvider:
    """
    Simple fallback provider when numpy / sentence-transformers / faiss are missing.
    - encode(texts): returns list of zero-vectors (python lists) of fixed small dim
    - add / search: no-op or return empty results
    This prevents server crash and keeps endpoints functional for demo.
    """
    def __init__(self, model_name="mock"):
        self.dim = 32
        self.model_name = model_name
        self._vectors = []  

    def encode(self, texts: List[str]):
        vecs = [[0.0] * self.dim for _ in texts]
        return vecs

    def add(self, vectors, metadatas=None):
        self._vectors.extend(vectors)

    def search(self, vectors, k=5):
        D = [[float("inf")] * k for _ in vectors]
        I = [[-1] * k for _ in vectors]
        return D, I

class EmbeddingProvider:
    """
    Real provider wrapper. Lazily loads heavy libs on first use.
    If imports fail, it falls back to MockEmbeddingProvider.
    """
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
        self._impl = None
        self._initialized = False

    def _init_impl(self):
        if self._initialized:
            return
        _try_imports()
        if _HAS_NUMPY and _HAS_SENT_TRANS and _HAS_FAISS:
            import numpy as np 
            from sentence_transformers import SentenceTransformer  
            import faiss  

            class RealImpl:
                def __init__(self, model_name, faiss_index_path="faiss.index"):
                    self.model = SentenceTransformer(model_name)
                    self.dim = self.model.get_sentence_embedding_dimension()
                    self.index_path = os.getenv("FAISS_INDEX_PATH", faiss_index_path)
                   
                    if os.path.exists(self.index_path):
                        self.index = faiss.read_index(self.index_path)
                    else:
                        self.index = faiss.IndexFlatL2(self.dim)

                def encode(self, texts: List[str]):
                    return np.array(self.model.encode(texts, show_progress_bar=False), dtype="float32")

                def add(self, vectors, metadatas=None):
                    self.index.add(vectors)
                    faiss.write_index(self.index, self.index_path)

                def search(self, vectors, k=5):
                    D, I = self.index.search(vectors, k)
                    return D, I

            self._impl = RealImpl(self.model_name)
        else:
            self._impl = MockEmbeddingProvider(self.model_name)
        self._initialized = True

    @property
    def dim(self):
        self._init_impl()
        return getattr(self._impl, "dim", 32)

    def encode(self, texts: List[str]):
        self._init_impl()
        return self._impl.encode(texts)

    def add(self, vectors, metadatas=None):
        self._init_impl()
        return self._impl.add(vectors, metadatas=metadatas)

    def search(self, vectors, k=5):
        self._init_impl()
        return self._impl.search(vectors, k)
