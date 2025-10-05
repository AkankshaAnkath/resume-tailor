from transformers import pipeline
from typing import List, Dict

class ContradictionChecker:
    def __init__(self):
        self.nli_model = pipeline("text-classification", model="cross-encoder/nli-deberta-v3-small")
    
    def check_contradiction(self, premise: str, hypothesis: str) -> Dict:
        result = self.nli_model(f"{premise} [SEP] {hypothesis}")[0]
        
        label = result["label"].lower()
        score = result["score"]
        
        is_contradiction = "contradiction" in label
        
        return {
            "is_contradiction": is_contradiction,
            "label": label,
            "confidence": score
        }
    
    def check_suggestion_against_resume(self, resume_facts: List[str], suggestion: str) -> Dict:
        contradictions = []
        
        for fact in resume_facts:
            check_result = self.check_contradiction(fact, suggestion)
            
            if check_result["is_contradiction"] and check_result["confidence"] > 0.7:
                contradictions.append({
                    "resume_fact": fact,
                    "suggestion": suggestion,
                    "confidence": check_result["confidence"]
                })
        
        has_contradiction = len(contradictions) > 0
        penalty = -0.05 * len(contradictions) if has_contradiction else 0.0
        
        return {
            "has_contradiction": has_contradiction,
            "contradictions": contradictions,
            "penalty": penalty
        }
    
    def extract_facts(self, resume_text: str) -> List[str]:
        sentences = resume_text.split('.')
        facts = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(char.isdigit() for char in sentence):
                facts.append(sentence)
        
        return facts