from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
import spacy

app = FastAPI(title="O1A Visa Assessor")

# Response Model
class CriteriaResult(BaseModel):
    criterion: str
    evidence: list[str]
    satisfied: bool

class VisaAssessment(BaseModel):
    criteria: list[CriteriaResult]
    rating: Literal["low", "medium", "high"]

# File Processing
SUPPORTED_TYPES = {"pdf", "docx", "txt"}

@app.post("/assess", response_model=VisaAssessment)
async def assess_o1a(cv: UploadFile):
    # Validate file type
    if cv.filename.split(".")[-1] not in SUPPORTED_TYPES:
        raise HTTPException(400, "Unsupported file type")
    
    # Process file
    raw_text = await process_file(cv)
    analysis = analyze_criteria(raw_text)
    rating = calculate_rating(analysis)
    
    return {
        "criteria": format_results(analysis),
        "rating": rating
    }
