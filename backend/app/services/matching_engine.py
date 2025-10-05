from typing import Dict, List, Tuple
from app.services.skill_extractor import SkillExtractor
from app.services.embedding_service import EmbeddingService
import re
from datetime import datetime

class MatchingEngine:
    def __init__(self, skill_extractor: SkillExtractor, embedding_service: EmbeddingService):
        self.skill_extractor = skill_extractor
        self.embedding_service = embedding_service
        
        self.weights = {
            "skills_exact": 0.40,
            "semantic_fit": 0.35,
            "seniority_fit": 0.15,
            "recency": 0.10
        }
        
        self.seniority_keywords = {
            "entry": ["junior", "entry level", "graduate", "intern", "associate", "trainee"],
            "mid": ["mid level", "intermediate", "engineer", "developer", "analyst", "specialist"],
            "senior": ["senior", "lead", "principal", "staff", "expert", "architect"],
            "executive": ["director", "vp", "vice president", "head of", "chief", "cto", "ceo", "executive"]
        }
        
        self.seniority_scores = {
            "entry": 1,
            "mid": 2,
            "senior": 3,
            "executive": 4
        }
    
    def compute_match_score(self, resume_data: Dict, jd_data: Dict) -> Dict:
        resume_skills = self.skill_extractor.extract_skills(resume_data["raw_text"])
        jd_skills = self.skill_extractor.extract_skills(jd_data["raw_text"])
        
        skills_exact_score = self._compute_skills_exact(resume_skills["all"], jd_skills["all"])
        
        semantic_fit_score, semantic_evidence = self._compute_semantic_fit(
            resume_data["sections"], 
            jd_data["requirements"]
        )
        
        seniority_fit_score = self._compute_seniority_fit(
            resume_data["raw_text"], 
            jd_data["raw_text"]
        )
        
        recency_score = self._compute_recency_score(resume_data["raw_text"])
        
        skill_overlap = self.skill_extractor.compute_skill_overlap(
            resume_skills["all"], 
            jd_skills["all"]
        )
        
        final_score = 100 * (
            self.weights["skills_exact"] * skills_exact_score +
            self.weights["semantic_fit"] * semantic_fit_score +
            self.weights["seniority_fit"] * seniority_fit_score +
            self.weights["recency"] * recency_score
        )
        
        return {
            "match_score": round(final_score, 2),
            "scores": {
                "skills_exact": round(skills_exact_score, 2),
                "semantic_fit": round(semantic_fit_score, 2),
                "seniority_fit": round(seniority_fit_score, 2),
                "recency": round(recency_score, 2),
                "contradiction_penalty": 0.0
            },
            "skill_overlap": skill_overlap,
            "semantic_evidence": semantic_evidence,
            "resume_skills": resume_skills,
            "jd_skills": jd_skills
        }
    
    def _compute_skills_exact(self, resume_skills: List[Dict], jd_skills: List[Dict]) -> float:
        if not jd_skills:
            return 1.0
        
        resume_ids = set(s["id"] for s in resume_skills)
        jd_ids = set(s["id"] for s in jd_skills)
        
        matched = len(resume_ids & jd_ids)
        total = len(jd_ids)
        
        return matched / total if total > 0 else 0.0
    
    def _compute_semantic_fit(self, resume_sections: List[Dict], jd_requirements: List[str]) -> Tuple[float, List[Dict]]:
        if not jd_requirements:
            return 1.0, []
        
        evidence = []
        total_similarity = 0.0
        matched_count = 0
        
        resume_texts = []
        for section in resume_sections:
            content = section.get("content", [])
            if isinstance(content, list):
                resume_texts.extend(content)
            else:
                resume_texts.append(content)
        
        for req_idx, requirement in enumerate(jd_requirements):
            best_match = {"similarity": 0.0, "text": "", "section": ""}
            
            for section in resume_sections:
                content = section.get("content", [])
                section_text = " ".join(content) if isinstance(content, list) else content
                
                if not section_text.strip():
                    continue
                
                similarity = self.embedding_service.compute_similarity(requirement, section_text)
                
                if similarity > best_match["similarity"]:
                    best_match = {
                        "similarity": similarity,
                        "text": section_text[:200],
                        "section": section.get("title", "unknown")
                    }
            
            if best_match["similarity"] > 0.5:
                matched_count += 1
                evidence.append({
                    "requirement": requirement,
                    "matched_section": best_match["section"],
                    "matched_text": best_match["text"],
                    "similarity": round(best_match["similarity"], 3)
                })
            
            total_similarity += best_match["similarity"]
        
        avg_similarity = total_similarity / len(jd_requirements) if jd_requirements else 0.0
        
        return avg_similarity, evidence
    
    def _compute_seniority_fit(self, resume_text: str, jd_text: str) -> float:
        resume_seniority = self._detect_seniority(resume_text)
        jd_seniority = self._detect_seniority(jd_text)
        
        resume_level = self.seniority_scores.get(resume_seniority, 2)
        jd_level = self.seniority_scores.get(jd_seniority, 2)
        
        difference = abs(resume_level - jd_level)
        
        if difference == 0:
            return 1.0
        elif difference == 1:
            return 0.8
        elif difference == 2:
            return 0.5
        else:
            return 0.3
    
    def _detect_seniority(self, text: str) -> str:
        text_lower = text.lower()
        
        seniority_counts = {level: 0 for level in self.seniority_keywords.keys()}
        
        for level, keywords in self.seniority_keywords.items():
            for keyword in keywords:
                count = text_lower.count(keyword)
                seniority_counts[level] += count
        
        if seniority_counts["executive"] > 0:
            return "executive"
        elif seniority_counts["senior"] >= 2:
            return "senior"
        elif seniority_counts["mid"] >= 2:
            return "mid"
        elif seniority_counts["entry"] >= 1:
            return "entry"
        
        return "mid"
    
    def _compute_recency_score(self, resume_text: str) -> float:
        current_year = datetime.now().year
        
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, resume_text)
        
        if not years:
            return 0.5
        
        years_int = [int(y) for y in years]
        most_recent = max(years_int)
        
        years_ago = current_year - most_recent
        
        if years_ago <= 1:
            return 1.0
        elif years_ago <= 2:
            return 0.9
        elif years_ago <= 3:
            return 0.7
        elif years_ago <= 5:
            return 0.5
        else:
            return 0.3
    
    def update_weights(self, new_weights: Dict[str, float]):
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        
        self.weights.update(new_weights)