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
        # Include top results for debugging and avoid false negatives from strict threshold.
        matches = [(self.chunks[i], float(scores[i])) for i in top]
        # By default return all top results; 0.1 threshold may help in low-sim situations.
        filtered = [m for m in matches if m[1] >= 0.1]
        return filtered if filtered else matches