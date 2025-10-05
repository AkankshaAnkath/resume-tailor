import spacy
import re
import csv
from typing import List, Dict, Set, Optional
from pathlib import Path
from fuzzywuzzy import fuzz

class SkillExtractor:
    def __init__(self, taxonomy_path: str = "data/esco_taxonomy"):
        self.nlp = spacy.load("en_core_web_sm")
        self.taxonomy_path = Path(taxonomy_path)
        
        self.skills_db = {}
        self.skill_synonyms = {}
        self.skill_patterns = {}
        
        self._load_taxonomy()
        self._build_patterns()
    
    def _load_taxonomy(self):
        skills_file = self.taxonomy_path / "skills.csv"
        synonyms_file = self.taxonomy_path / "skill_synonyms.csv"
        
        if skills_file.exists():
            with open(skills_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill_id = row["id"]
                    self.skills_db[skill_id] = {
                        "name": row["name"].lower(),
                        "type": row["type"],
                        "category": row["category"]
                    }
        
        if synonyms_file.exists():
            with open(synonyms_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill_id = row["skill_id"]
                    synonym = row["synonym"].lower()
                    if skill_id not in self.skill_synonyms:
                        self.skill_synonyms[skill_id] = []
                    self.skill_synonyms[skill_id].append(synonym)
    
    def _build_patterns(self):
        for skill_id, skill_data in self.skills_db.items():
            terms = [skill_data["name"]]
            if skill_id in self.skill_synonyms:
                terms.extend(self.skill_synonyms[skill_id])
            
            self.skill_patterns[skill_id] = [
                re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                for term in terms
            ]
    
    def extract_skills(self, text: str, min_confidence: float = 0.8) -> Dict[str, List[Dict]]:
        text_lower = text.lower()
        detected_skills = []
        
        for skill_id, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text_lower)
                if matches:
                    skill_data = self.skills_db[skill_id]
                    detected_skills.append({
                        "id": skill_id,
                        "name": skill_data["name"],
                        "type": skill_data["type"],
                        "category": skill_data["category"],
                        "confidence": 1.0,
                        "matched_term": matches[0]
                    })
                    break
        
        doc = self.nlp(text)
        
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        for phrase in noun_phrases:
            for skill_id, skill_data in self.skills_db.items():
                skill_name = skill_data["name"]
                similarity = fuzz.ratio(phrase, skill_name) / 100.0
                
                if similarity >= min_confidence:
                    if not any(s["id"] == skill_id for s in detected_skills):
                        detected_skills.append({
                            "id": skill_id,
                            "name": skill_name,
                            "type": skill_data["type"],
                            "category": skill_data["category"],
                            "confidence": similarity,
                            "matched_term": phrase
                        })
        
        technical = [s for s in detected_skills if s["type"] == "technical"]
        soft = [s for s in detected_skills if s["type"] == "soft"]
        
        return {
            "technical": technical,
            "soft": soft,
            "all": detected_skills
        }
    
    def extract_years_of_experience(self, text: str) -> Dict[str, Dict]:
        experience_map = {}
        
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience\s+)?(?:with\s+|in\s+)?([a-zA-Z\s.+-]+)',
            r'([a-zA-Z\s.+-]+)[\s:]+(\d+)\+?\s*years?',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.lastindex == 2:
                    years = match.group(1) if match.group(1).isdigit() else match.group(2)
                    skill = match.group(2) if match.group(1).isdigit() else match.group(1)
                    
                    skill_clean = skill.strip().lower()
                    if skill_clean and years.isdigit():
                        matched_skill = self._match_to_taxonomy(skill_clean)
                        if matched_skill:
                            experience_map[matched_skill["id"]] = {
                                "years": int(years),
                                "skill_name": matched_skill["name"],
                                "original_text": skill_clean
                            }
        
        return experience_map
    
    def _match_to_taxonomy(self, skill_text: str) -> Optional[Dict]:
        for skill_id, skill_data in self.skills_db.items():
            if skill_data["name"] in skill_text:
                return {"id": skill_id, "name": skill_data["name"]}
            
            if skill_id in self.skill_synonyms:
                for syn in self.skill_synonyms[skill_id]:
                    if syn in skill_text:
                        return {"id": skill_id, "name": skill_data["name"]}
        
        return None
    
    def compute_skill_overlap(self, resume_skills: List[Dict], jd_skills: List[Dict]) -> Dict:
        resume_ids = set(s["id"] for s in resume_skills)
        jd_ids = set(s["id"] for s in jd_skills)
        
        matched_ids = resume_ids & jd_ids
        missing_ids = jd_ids - resume_ids
        extra_ids = resume_ids - jd_ids
        
        matched = [s for s in jd_skills if s["id"] in matched_ids]
        missing = [s for s in jd_skills if s["id"] in missing_ids]
        extra = [s for s in resume_skills if s["id"] in extra_ids]
        
        overlap_score = len(matched_ids) / len(jd_ids) if jd_ids else 0.0
        
        return {
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "overlap_score": overlap_score,
            "matched_count": len(matched_ids),
            "total_required": len(jd_ids)
        }
    
    def add_custom_skill(self, skill_id: str, name: str, skill_type: str, category: str, synonyms: List[str] = None):
        self.skills_db[skill_id] = {
            "name": name.lower(),
            "type": skill_type,
            "category": category
        }
        
        if synonyms:
            self.skill_synonyms[skill_id] = [s.lower() for s in synonyms]
        
        self._build_patterns()