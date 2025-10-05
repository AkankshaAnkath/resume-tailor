import fitz
import pytesseract
from PIL import Image
import io
import base64
from typing import Dict, List, Tuple
import re

class PDFParser:
    def __init__(self):
        self.column_threshold = 100
        
    def parse_pdf_from_base64(self, pdf_b64: str) -> Dict:
        pdf_bytes = base64.b64decode(pdf_b64)
        return self.parse_pdf_from_bytes(pdf_bytes)
    
    def parse_pdf_from_bytes(self, pdf_bytes: bytes) -> Dict:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        full_text = []
        sections = []
        layout_warnings = []
        has_multiple_columns = False
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if b["type"] == 0]
            
            if self._detect_columns(text_blocks):
                has_multiple_columns = True
                layout_warnings.append("Multi-column layout detected on page " + str(page_num + 1))
            
            page_text = page.get_text("text")
            
            if not page_text.strip():
                ocr_text = self._ocr_page(page)
                page_text = ocr_text
                if ocr_text:
                    layout_warnings.append("OCR used on page " + str(page_num + 1))
            
            full_text.append(page_text)
        
        doc.close()
        
        combined_text = "\n".join(full_text)
        sections = self._extract_sections(combined_text)
        
        return {
            "raw_text": combined_text,
            "sections": sections,
            "layout_warnings": layout_warnings,
            "metadata": {
                "has_multiple_columns": has_multiple_columns,
                "page_count": len(doc)
            }
        }
    
    def _detect_columns(self, blocks: List[Dict]) -> bool:
        if len(blocks) < 2:
            return False
        
        x_positions = [b["bbox"][0] for b in blocks]
        x_positions.sort()
        
        gaps = []
        for i in range(1, len(x_positions)):
            gap = x_positions[i] - x_positions[i-1]
            if gap > self.column_threshold:
                gaps.append(gap)
        
        return len(gaps) > 0
    
    def _ocr_page(self, page) -> str:
        try:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception:
            return ""
    
    def _extract_sections(self, text: str) -> List[Dict]:
        sections = []
        
        section_headers = [
            r"(?i)^(summary|profile|objective)",
            r"(?i)^(experience|work experience|employment)",
            r"(?i)^(education|academic)",
            r"(?i)^(skills|technical skills|core competencies)",
            r"(?i)^(projects|key projects)",
            r"(?i)^(certifications|certificates)",
            r"(?i)^(awards|achievements|honors)",
        ]
        
        lines = text.split("\n")
        current_section = {"title": "header", "content": []}
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            is_header = False
            for pattern in section_headers:
                if re.match(pattern, line_stripped):
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