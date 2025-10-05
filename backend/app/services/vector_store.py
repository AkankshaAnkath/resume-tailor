import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from app.core.config import settings as app_settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=app_settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        self.resume_collection = self.client.get_or_create_collection(
            name="resume_sections",
            metadata={"hnsw:space": "cosine"}
        )
        self.jd_collection = self.client.get_or_create_collection(
            name="jd_requirements",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_resume_sections(self, sections: List[Dict], embeddings: List[List[float]], resume_id: str):
        ids = [f"{resume_id}_section_{i}" for i in range(len(sections))]
        documents = [s.get("content", "") if isinstance(s.get("content"), str) else " ".join(s.get("content", [])) for s in sections]
        metadatas = [{"resume_id": resume_id, "title": s.get("title", ""), "section_index": i} for i, s in enumerate(sections)]
        
        self.resume_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def add_jd_requirements(self, requirements: List[str], embeddings: List[List[float]], jd_id: str):
        ids = [f"{jd_id}_req_{i}" for i in range(len(requirements))]
        metadatas = [{"jd_id": jd_id, "req_index": i} for i in range(len(requirements))]
        
        self.jd_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=requirements,
            metadatas=metadatas
        )
    
    def query_similar_sections(self, query_embedding: List[float], n_results: int = 5) -> Dict:
        results = self.resume_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    
    def query_similar_requirements(self, query_embedding: List[float], n_results: int = 5) -> Dict:
        results = self.jd_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    
    def clear_resume(self, resume_id: str):
        try:
            results = self.resume_collection.get(where={"resume_id": resume_id})
            if results["ids"]:
                self.resume_collection.delete(ids=results["ids"])
        except Exception:
            pass
    
    def clear_jd(self, jd_id: str):
        try:
            results = self.jd_collection.get(where={"jd_id": jd_id})
            if results["ids"]:
                self.jd_collection.delete(ids=results["ids"])
        except Exception:
            pass