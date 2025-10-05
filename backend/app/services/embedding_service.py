from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List, Dict
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def embed_single(self, text: str) -> np.ndarray:
        return self.embedding_model.encode([text], convert_to_numpy=True)[0]
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        emb1 = self.embed_single(text1)
        emb2 = self.embed_single(text2)
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    
    def compute_similarities_batch(self, query: str, documents: List[str]) -> List[float]:
        query_emb = self.embed_single(query)
        doc_embs = self.embed_texts(documents)
        
        similarities = []
        for doc_emb in doc_embs:
            sim = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
            similarities.append(float(sim))
        
        return similarities
    
    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        pairs = [[query, doc] for doc in documents]
        scores = self.reranker.predict(pairs)
        
        results = []
        for idx, score in enumerate(scores):
            results.append({
                "text": documents[idx],
                "score": float(score),
                "index": idx
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def find_most_similar(self, query: str, candidates: List[str], threshold: float = 0.5) -> List[Dict]:
        similarities = self.compute_similarities_batch(query, candidates)
        
        results = []
        for idx, sim in enumerate(similarities):
            if sim >= threshold:
                results.append({
                    "text": candidates[idx],
                    "similarity": sim,
                    "index": idx
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results