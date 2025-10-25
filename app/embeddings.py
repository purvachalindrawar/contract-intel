# app/embeddings.py
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss.index")
MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

class EmbeddingProvider:
    def __init__(self, model_name=MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        if os.path.exists(FAISS_INDEX_PATH):
            self.index = faiss.read_index(FAISS_INDEX_PATH)
        else:
            self.index = faiss.IndexFlatL2(self.dim)

    def encode(self, texts):
        return np.array(self.model.encode(texts, show_progress_bar=False), dtype="float32")

    def add(self, vectors):
        self.index.add(vectors)
        faiss.write_index(self.index, FAISS_INDEX_PATH)

    def search(self, vectors, k=5):
        D, I = self.index.search(vectors, k)
        return D, I
