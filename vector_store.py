import numpy as np
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self):
        print("Loading embedding model (first run downloads ~90MB)...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = []
        self.embeddings = None

    def add(self, chunks):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        self.embeddings = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=True
        )

    def search(self, query, top_k=5):
        if self.embeddings is None:
            return []
        q = self.model.encode(query, normalize_embeddings=True)
        scores = self.embeddings @ q
        top = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in top if scores[i] > 0.3]