from typing import Dict, List, Optional
from app.services.llm_service import LLMService
from app.services.contradiction_checker import ContradictionChecker
import json

class RewriteAgent:
    def __init__(self, llm_service: LLMService, contradiction_checker: ContradictionChecker):
        self.llm = llm_service
        self.contradiction_checker = contradiction_checker
    
    def generate_suggestions(self, resume_data: Dict, jd_data: Dict, match_results: Dict) -> List[Dict]:
        resume_facts = self._extract_resume_facts(resume_data)
        missing_skills = match_results["skill_overlap"]["missing"]
        semantic_evidence = match_results.get("semantic_evidence", [])
        
        suggestions = []
        
        for skill in missing_skills[:5]:
            suggestion = self._suggest_skill_addition(skill, resume_facts, jd_data)
            if suggestion:
                suggestions.append(suggestion)
        
        for evidence in semantic_evidence[:3]:
            if evidence["similarity"] < 0.7:
                suggestion = self._suggest_content_improvement(evidence, resume_facts, jd_data)
                if suggestion:
                    suggestions.append(suggestion)
        
        validated_suggestions = []
        for suggestion in suggestions:
            if self._validate_suggestion(suggestion, resume_facts):
                validated_suggestions.append(suggestion)
        
        return validated_suggestions
    
    def _extract_resume_facts(self, resume_data: Dict) -> List[str]:
        facts = []
        
        for section in resume_data.get("sections", []):
            content = section.get("content", [])
            if isinstance(content, list):
                facts.extend(content)
            else:
                facts.append(content)
        
        return [f for f in facts if len(f) > 20]
    
    def _suggest_skill_addition(self, skill: Dict, resume_facts: List[str], jd_data: Dict) -> Optional[Dict]:
        system_prompt = """You are a resume improvement assistant. Generate suggestions to add missing skills based ONLY on existing resume content.
Rules:
1. Only suggest rephrasing existing content to highlight the skill
2. NEVER invent new achievements or experiences
3. If the skill cannot be derived from existing content, return null
4. Output valid JSON only"""
        
        user_prompt = f"""Resume Facts:
{json.dumps(resume_facts[:10], indent=2)}

Missing Skill: {skill['name']}
Job Requirement Context: {jd_data['raw_text'][:500]}

Task: Suggest how to rephrase ONE existing resume fact to highlight this skill, or return null if impossible.

Output JSON format:
{{
  "before": "original resume text",
  "after": "improved text highlighting the skill",
  "reasoning": "why this change helps",
  "confidence": 0.0-1.0,
  "skill_id": "{skill['id']}"
}}"""
        
        try:
            response = self.llm.generate_json(user_prompt, system_prompt)
            
            if response and "before" in response and response.get("before"):
                return {
                    "before": response["before"],
                    "after": response["after"],
                    "reasoning": response.get("reasoning", ""),
                    "confidence": response.get("confidence", 0.5),
                    "grounded_by": [0],
                    "type": "skill_addition",
                    "skill_id": skill["id"]
                }
        except Exception:
            pass
        
        return None
    
    def _suggest_content_improvement(self, evidence: Dict, resume_facts: List[str], jd_data: Dict) -> Optional[Dict]:
        system_prompt = """You are a resume improvement assistant. Improve existing resume content to better match job requirements.
Rules:
1. Only modify existing content, never add new facts
2. Maintain truthfulness
3. Improve clarity and impact
4. Output valid JSON only"""
        
        matched_text = evidence.get("matched_text", "")
        requirement = evidence.get("requirement", "")
        
        user_prompt = f"""Resume Content:
{matched_text}

Job Requirement:
{requirement}

Current Similarity: {evidence.get('similarity', 0)}

Task: Improve the resume content to better match the requirement while staying factual.

Output JSON format:
{{
  "before": "original text",
  "after": "improved text",
  "reasoning": "explanation of improvement",
  "confidence": 0.0-1.0
}}"""
        
        try:
            response = self.llm.generate_json(user_prompt, system_prompt)
            
            if response and "before" in response and response.get("before"):
                return {
                    "before": response["before"],
                    "after": response["after"],
                    "reasoning": response.get("reasoning", ""),
                    "confidence": response.get("confidence", 0.5),
                    "grounded_by": [0],
                    "type": "content_improvement"
                }
        except Exception:
            pass
        
        return None
    
    def _validate_suggestion(self, suggestion: Dict, resume_facts: List[str]) -> bool:
        if not suggestion.get("after"):
            return False
        
        contradiction_result = self.contradiction_checker.check_suggestion_against_resume(
            resume_facts,
            suggestion["after"]
        )
        
        if contradiction_result["has_contradiction"]:
            return False
        
        if suggestion.get("confidence", 0) < 0.3:
            return False
        
        return True
    
    def generate_bullet_improvements(self, bullets: List[str], jd_data: Dict) -> List[Dict]:
        system_prompt = """You are a resume bullet point optimizer. Improve bullet points for impact and ATS optimization.
Rules:
1. Start with strong action verbs
2. Include quantifiable metrics when present
3. Align with job requirements
4. Keep factual, never add fake numbers
5. Output valid JSON only"""
        
        user_prompt = f"""Bullet Points:
{json.dumps(bullets, indent=2)}

Job Description:
{jd_data['raw_text'][:800]}

Task: Improve each bullet point for clarity, impact, and job alignment.

Output JSON format:
{{
  "improvements": [
    {{
      "before": "original bullet",
      "after": "improved bullet",
      "reasoning": "what was improved"
    }}
  ]
}}"""
        
        try:
            response = self.llm.generate_json(user_prompt, system_prompt)
            return response.get("improvements", [])
        except Exception:
            return []