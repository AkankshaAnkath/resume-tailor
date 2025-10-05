from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from typing import Dict, List

class PIIService:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        self.entity_types = [
            "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", 
            "CREDIT_CARD", "IBAN_CODE", "US_SSN",
            "US_PASSPORT", "LOCATION", "DATE_TIME",
            "IP_ADDRESS", "URL"
        ]
        
        self.anonymize_config = {
            "PERSON": OperatorConfig("replace", {"new_value": "[NAME]"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "[CREDIT_CARD]"}),
            "US_SSN": OperatorConfig("replace", {"new_value": "[SSN]"}),
        }
    
    def detect_pii(self, text: str, language: str = "en") -> List[Dict]:
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=self.entity_types
        )
        
        pii_found = []
        for result in results:
            pii_found.append({
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start:result.end]
            })
        
        return pii_found
    
    def redact_pii(self, text: str, language: str = "en") -> Dict:
        analyzer_results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=self.entity_types
        )
        
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=self.anonymize_config
        )
        
        return {
            "original_text": text,
            "redacted_text": anonymized_result.text,
            "items_redacted": len(analyzer_results),
            "pii_types": list(set([r.entity_type for r in analyzer_results]))
        }
    
    def selective_redact(self, text: str, keep_entities: List[str] = None, language: str = "en") -> str:
        if keep_entities is None:
            keep_entities = []
        
        redact_entities = [e for e in self.entity_types if e not in keep_entities]
        
        analyzer_results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=redact_entities
        )
        
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=self.anonymize_config
        )
        
        return anonymized_result.text
    
    def redact_resume_for_sharing(self, resume_text: str) -> Dict:
        keep_entities = ["DATE_TIME", "LOCATION"]
        
        redacted_text = self.selective_redact(resume_text, keep_entities=keep_entities)
        
        pii_found = self.detect_pii(resume_text)
        
        return {
            "redacted_text": redacted_text,
            "pii_detected": pii_found,
            "safe_for_sharing": len([p for p in pii_found if p["entity_type"] not in keep_entities]) == 0
        }