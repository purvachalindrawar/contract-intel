# app/retriever.py
from .embeddings import EmbeddingProvider

class Retriever:
    def __init__(self):
        self.ep = EmbeddingProvider()

    def add_texts(self, texts):
        vecs = self.ep.encode(texts)
        self.ep.add(vecs)

    def query(self, question, k=3):
        qvec = self.ep.encode([question])
        D, I = self.ep.search(qvec, k)
        return {"distances": D.tolist(), "indices": I.tolist()}
