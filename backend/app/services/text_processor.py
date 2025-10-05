import re
from typing import Dict, List

class TextProcessor:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        self.url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+')
        
    def process_jd_text(self, jd_text: str) -> Dict:
        sections = self._split_jd_sections(jd_text)
        requirements = self._extract_requirements(jd_text)
        
        return {
            "raw_text": jd_text,
            "sections": sections,
            "requirements": requirements,
            "metadata": {
                "word_count": len(jd_text.split()),
                "char_count": len(jd_text)
            }
        }
    
    def _split_jd_sections(self, text: str) -> List[Dict]:
        sections = []
        
        section_patterns = [
            r"(?i)(about|company|overview)",
            r"(?i)(role|position|job description)",
            r"(?i)(responsibilities|duties|what you.?ll do)",
            r"(?i)(requirements|qualifications|what we.?re looking for)",
            r"(?i)(preferred|nice to have|bonus)",
            r"(?i)(benefits|perks|what we offer)",
        ]
        
        lines = text.split("\n")
        current_section = {"title": "overview", "content": []}
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            is_header = False
            for pattern in section_patterns:
                if re.search(pattern, line_stripped) and len(line_stripped) < 100:
                    if current_section["content"]:
                        sections.append(current_section)
                    current_section = {"title": line_stripped.lower(), "content": []}
                    is_header = True
                    break
            
            if not is_header:
                current_section["content"].append(line_stripped)
        
        if current_section["content"]:
            sections.append(current_section)
        
        return sections
    
    def _extract_requirements(self, text: str) -> List[str]:
        requirements = []
        
        lines = text.split("\n")
        in_requirements = False
        
        for line in lines:
            line_stripped = line.strip()
            
            if re.search(r"(?i)(requirements|qualifications|must have)", line_stripped):
                in_requirements = True
                continue
            
            if re.search(r"(?i)(benefits|perks|about)", line_stripped):
                in_requirements = False
            
            if in_requirements and line_stripped:
                cleaned = re.sub(r'^[-•*]\s*', '', line_stripped)
                if len(cleaned) > 10:
                    requirements.append(cleaned)
        
        return requirements
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def extract_contact_info(self, text: str) -> Dict:
        emails = self.email_pattern.findall(text)
        phones = self.phone_pattern.findall(text)
        urls = self.url_pattern.findall(text)
        
        return {
            "emails": list(set(emails)),
            "phones": list(set(phones)),
            "urls": list(set(urls))
        }