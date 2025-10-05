from typing import Dict, List
import re

class EvidenceBuilder:
    def __init__(self):
        self.max_quote_length = 200
    
    def build_evidence(self, resume_data: Dict, jd_data: Dict, match_results: Dict) -> List[Dict]:
        evidence_list = []
        
        skill_overlap = match_results.get("skill_overlap", {})
        for skill in skill_overlap.get("matched", []):
            resume_quote = self._find_skill_context(skill["name"], resume_data["raw_text"])
            jd_quote = self._find_skill_context(skill["name"], jd_data["raw_text"])
            
            if resume_quote and jd_quote:
                evidence_list.append({
                    "type": "skill_match",
                    "skill": skill["name"],
                    "skill_id": skill["id"],
                    "resume_quote": resume_quote,
                    "jd_quote": jd_quote,
                    "confidence": skill.get("confidence", 1.0)
                })
        
        semantic_evidence = match_results.get("semantic_evidence", [])
        for sem_match in semantic_evidence:
            evidence_list.append({
                "type": "semantic_match",
                "requirement": sem_match["requirement"],
                "resume_section": sem_match["matched_section"],
                "resume_quote": sem_match["matched_text"],
                "similarity": sem_match["similarity"]
            })
        
        return evidence_list
    
    def _find_skill_context(self, skill_name: str, text: str, context_window: int = 100) -> str:
        pattern = re.compile(r'\b' + re.escape(skill_name) + r'\b', re.IGNORECASE)
        match = pattern.search(text)
        
        if not match:
            return ""
        
        start = max(0, match.start() - context_window)
        end = min(len(text), match.end() + context_window)
        
        context = text[start:end].strip()
        
        if len(context) > self.max_quote_length:
            context = context[:self.max_quote_length] + "..."
        
        return context
    
    def create_citation(self, evidence: Dict) -> str:
        if evidence["type"] == "skill_match":
            return f"Skill '{evidence['skill']}' found in resume and matches JD requirement"
        elif evidence["type"] == "semantic_match":
            return f"Resume section '{evidence['resume_section']}' semantically matches requirement"
        return ""