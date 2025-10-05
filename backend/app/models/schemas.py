from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class AnalyzeRequest(BaseModel):
    resume_pdf_b64: str
    jd_text: str
    options: Optional[Dict] = Field(default_factory=dict)

class Evidence(BaseModel):
    source: str
    quote: str

class Suggestion(BaseModel):
    before: str
    after: str
    grounded_by: List[int]
    reasoning: str
    confidence: float

class ScoreBreakdown(BaseModel):
    skills_exact: float
    semantic_fit: float
    seniority_fit: float
    recency: float
    contradiction_penalty: float

class AnalyzeResponse(BaseModel):
    match_score: float
    scores: ScoreBreakdown
    missing_skills: List[str]
    evidence: List[Evidence]
    suggestions: List[Suggestion]
    ats_preview_text: str
    layout_warnings: List[str]

class SuggestRequest(BaseModel):
    resume_json: Dict
    jd_json: Dict
    match_data: Dict

class SuggestResponse(BaseModel):
    suggestions: List[Suggestion]
    
class ExportRequest(BaseModel):
    resume_json: Dict
    suggestions: List[Dict]
    format: str = "pdf"

class ExportResponse(BaseModel):
    file_b64: str
    filename: str