from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, SuggestRequest, SuggestResponse, ExportRequest, ExportResponse
from app.services import (PDFParser, TextProcessor, SkillExtractor, EmbeddingService, 
                          VectorStore, MatchingEngine, EvidenceBuilder, ContradictionChecker,
                          LLMService, RewriteAgent, PIIService, ObservabilityService, PDFGenerator)
from app.utils.logger import get_logger
import uuid
import base64

router = APIRouter()
logger = get_logger(__name__)

pdf_parser = PDFParser()
text_processor = TextProcessor()
skill_extractor = SkillExtractor()
embedding_service = EmbeddingService()
vector_store = VectorStore()
matching_engine = MatchingEngine(skill_extractor, embedding_service)
evidence_builder = EvidenceBuilder()
contradiction_checker = ContradictionChecker()
llm_service = LLMService()
rewrite_agent = RewriteAgent(llm_service, contradiction_checker)
pii_service = PIIService()
obs_service = ObservabilityService()
pdf_generator = PDFGenerator()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    trace = obs_service.create_trace(name="analyze_resume", metadata={"endpoint": "/analyze"})
    
    try:
        logger.info("Starting resume analysis")
        
        resume_data = pdf_parser.parse_pdf_from_base64(request.resume_pdf_b64)
        jd_data = text_processor.process_jd_text(request.jd_text)
        
        pii_detected = pii_service.detect_pii(resume_data["raw_text"])
        if pii_detected:
            logger.info(f"PII detected: {len(pii_detected)} items")
        
        match_results = matching_engine.compute_match_score(resume_data, jd_data)
        
        evidence_list = evidence_builder.build_evidence(resume_data, jd_data, match_results)
        
        suggestions = rewrite_agent.generate_suggestions(resume_data, jd_data, match_results)
        
        evidence_response = [
            {"source": "resume" if "resume" in str(e) else "jd", "quote": e.get("resume_quote", e.get("jd_quote", ""))}
            for e in evidence_list[:10]
        ]
        
        missing_skills = [skill["name"] for skill in match_results["skill_overlap"]["missing"]]
        
        suggestions_response = [
            {
                "before": s["before"],
                "after": s["after"],
                "grounded_by": s.get("grounded_by", []),
                "reasoning": s.get("reasoning", ""),
                "confidence": s.get("confidence", 0.5)
            }
            for s in suggestions
        ]
        
        logger.info(f"Analysis complete. Match score: {match_results['match_score']}")
        
        obs_service.flush()
        
        return AnalyzeResponse(
            match_score=match_results["match_score"],
            scores=match_results["scores"],
            missing_skills=missing_skills,
            evidence=evidence_response,
            suggestions=suggestions_response,
            ats_preview_text=resume_data["raw_text"],
            layout_warnings=resume_data["layout_warnings"]
        )
    except Exception as e:
        logger.error(f"Error in analyze_resume: {str(e)}")
        obs_service.log_error(trace, e, {"endpoint": "/analyze"})
        obs_service.flush()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest", response_model=SuggestResponse)
async def generate_suggestions(request: SuggestRequest):
    try:
        suggestions = rewrite_agent.generate_suggestions(
            request.resume_json,
            request.jd_json,
            request.match_data
        )
        
        suggestions_response = [
            {
                "before": s["before"],
                "after": s["after"],
                "grounded_by": s.get("grounded_by", []),
                "reasoning": s.get("reasoning", ""),
                "confidence": s.get("confidence", 0.5)
            }
            for s in suggestions
        ]
        
        return SuggestResponse(suggestions=suggestions_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export", response_model=ExportResponse)
async def export_resume(request: ExportRequest):
    try:
        logger.info(f"Exporting resume in format: {request.format}")
        
        suggestions = [
            {
                "before": s.get("before", ""),
                "after": s.get("after", "")
            }
            for s in request.suggestions
        ]
        
        if request.format == "pdf":
            pdf_bytes = pdf_generator.generate_tailored_resume(request.resume_json, suggestions)
            pdf_b64 = pdf_generator.pdf_to_base64(pdf_bytes)
            
            return ExportResponse(
                file_b64=pdf_b64,
                filename="resume_tailored.pdf"
            )
        
        elif request.format == "ats":
            ats_text = pdf_generator.generate_ats_text(request.resume_json, suggestions)
            ats_b64 = base64.b64encode(ats_text.encode()).decode()
            
            return ExportResponse(
                file_b64=ats_b64,
                filename="resume_tailored_ats.txt"
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
            
    except Exception as e:
        logger.error(f"Error in export_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))