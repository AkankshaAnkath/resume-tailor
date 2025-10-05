from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO
import base64
from typing import Dict, List

class PDFGenerator:
    def __init__(self):
        self.page_width, self.page_height = letter
        self.styles = getSampleStyleSheet()
        
        self.styles.add(ParagraphStyle(
            name='ResumeHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor='#2c3e50'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor='#34495e',
            borderWidth=1,
            borderColor='#bdc3c7',
            borderPadding=4
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6
        ))
    
    def generate_tailored_resume(self, resume_data: Dict, suggestions: List[Dict]) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, 
                               leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        
        applied_suggestions = self._apply_suggestions_to_resume(resume_data, suggestions)
        
        sections = applied_suggestions.get("sections", [])
        
        for section in sections:
            section_title = section.get("title", "").upper()
            if section_title:
                story.append(Paragraph(section_title, self.styles['SectionHeading']))
                story.append(Spacer(1, 0.2*inch))
            
            content = section.get("content", [])
            if isinstance(content, list):
                for item in content:
                    bullet = Paragraph(f"• {item}", self.styles['BulletPoint'])
                    story.append(bullet)
            else:
                para = Paragraph(content, self.styles['Normal'])
                story.append(para)
            
            story.append(Spacer(1, 0.3*inch))
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _apply_suggestions_to_resume(self, resume_data: Dict, suggestions: List[Dict]) -> Dict:
        sections = resume_data.get("sections", [])
        modified_sections = []
        
        for section in sections:
            modified_section = {
                "title": section.get("title", ""),
                "content": []
            }
            
            content = section.get("content", [])
            if isinstance(content, list):
                for item in content:
                    modified_item = item
                    
                    for suggestion in suggestions:
                        if suggestion.get("before", "") in item:
                            modified_item = item.replace(
                                suggestion["before"], 
                                suggestion["after"]
                            )
                            break
                    
                    modified_section["content"].append(modified_item)
            else:
                modified_section["content"] = content
            
            modified_sections.append(modified_section)
        
        return {
            "raw_text": resume_data.get("raw_text", ""),
            "sections": modified_sections
        }
    
    def generate_ats_text(self, resume_data: Dict, suggestions: List[Dict]) -> str:
        applied_resume = self._apply_suggestions_to_resume(resume_data, suggestions)
        
        ats_lines = []
        
        for section in applied_resume.get("sections", []):
            title = section.get("title", "").upper()
            if title:
                ats_lines.append(title)
                ats_lines.append("")
            
            content = section.get("content", [])
            if isinstance(content, list):
                for item in content:
                    ats_lines.append(item)
            else:
                ats_lines.append(content)
            
            ats_lines.append("")
        
        return "\n".join(ats_lines)
    
    def pdf_to_base64(self, pdf_bytes: bytes) -> str:
        return base64.b64encode(pdf_bytes).decode('utf-8')