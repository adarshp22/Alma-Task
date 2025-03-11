# o1a_assessor.py
import io
from typing import List, Literal
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
import spacy
from spacy.matcher import Matcher
from pdfminer.high_level import extract_text as extract_pdf_text
import docx2txt

# Initialize FastAPI app
app = FastAPI(
    title="O-1A Visa Eligibility Assessor",
    description="AI-powered O-1A visa qualification assessment system",
    version="1.0.0"
)

# Load NLP model
nlp = spacy.load("en_core_web_lg")
matcher = Matcher(nlp.vocab)

# Configure matching patterns
CRITERIA_PATTERNS = {
    "awards": [
        [{"LOWER": {"IN": ["award", "prize", "medal"]}}, {"ENT_TYPE": "ORG"}]
    ],
    "memberships": [
        [{"LOWER": "member"}, {"LOWER": "of"}, {"ENT_TYPE": "ORG"}],
        [{"LOWER": "fellow"}, {"LOWER": "of"}, {"ENT_TYPE": "ORG"}]
    ],
    "press": [
        [{"ENT_TYPE": "ORG"}, {"LOWER": "interview"}, {"LOWER": "with"}],
        [{"LOWER": "featured"}, {"LOWER": "in"}, {"ENT_TYPE": "ORG"}]
    ],
    "judging": [
        [{"LEMMA": {"IN": ["review", "judge", "evaluate"]}}, {"LOWER": "submissions"}],
        [{"LOWER": "program"}, {"LOWER": "committee"}, {"ENT_TYPE": "ORG"}]
    ]
}

for criterion, patterns in CRITERIA_PATTERNS.items():
    matcher.add(criterion.upper(), patterns)

# Configure weights and thresholds
CRITERIA_WEIGHTS = {
    "awards": 0.25,
    "original_contribution": 0.20,
    "scholarly_articles": 0.15,
    "high_remuneration": 0.15,
    "memberships": 0.10,
    "press": 0.07,
    "judging": 0.05,
    "critical_employment": 0.03
}

RATING_THRESHOLDS = {
    "low": 0.4,
    "medium": 0.7
}

# Pydantic models
class CriterionResult(BaseModel):
    criterion: str
    evidence: List[str]
    satisfied: bool

class VisaAssessment(BaseModel):
    criteria: List[CriterionResult]
    rating: Literal["low", "medium", "high"]

# Helper functions
async def process_file(file: UploadFile) -> str:
    """Process uploaded file and extract text"""
    content = await file.read()
    
    if file.filename.endswith(".pdf"):
        try:
            return extract_pdf_text(io.BytesIO(content))
        except:
            raise HTTPException(400, "Invalid PDF file")
            
    elif file.filename.endswith(".docx"):
        try:
            return docx2txt.process(io.BytesIO(content))
        except:
            raise HTTPException(400, "Invalid DOCX file")
            
    elif file.filename.endswith(".txt"):
        return content.decode("utf-8")
        
    raise HTTPException(400, "Unsupported file type")

def analyze_criteria(text: str) -> dict:
    """Analyze text for O-1A criteria matches"""
    doc = nlp(text.lower())
    matches = matcher(doc)
    
    results = {criterion: [] for criterion in CRITERIA_WEIGHTS.keys()}
    
    # Handle pattern matches
    for match_id, start, end in matches:
        criterion = nlp.vocab.strings[match_id].lower()
        results[criterion].append(doc[start:end].text)
    
    # Additional analysis for other criteria
    results["scholarly_articles"] = [ent.text for ent in doc.ents if ent.label_ == "WORK_OF_ART"]
    results["high_remuneration"] = extract_salary_info(doc)
    
    return results

def extract_salary_info(doc) -> List[str]:
    """Extract salary information using rule-based matching"""
    salary_phrases = []
    money_pattern = [{"ENT_TYPE": "MONEY"}]
    
    money_matcher = Matcher(nlp.vocab)
    money_matcher.add("MONEY", [money_pattern])
    
    for match_id, start, end in money_matcher(doc):
        phrase = doc[start-2:end+2].text  # Get context around money
        if any(word in phrase for word in ["salary", "compensation", "earned"]):
            salary_phrases.append(phrase)
    
    return salary_phrases

def calculate_rating(analysis: dict) -> str:
    """Calculate final rating based on criteria matches"""
    total_score = sum(
        CRITERIA_WEIGHTS[criterion] * (1 if len(evidence) > 0 else 0)
        for criterion, evidence in analysis.items()
    )
    
    if total_score >= RATING_THRESHOLDS["medium"]:
        return "high"
    elif total_score >= RATING_THRESHOLDS["low"]:
        return "medium"
    return "low"

# API Endpoint
@app.post("/assess", response_model=VisaAssessment)
async def assess_o1a_eligibility(cv: UploadFile):
    """Main assessment endpoint"""
    try:
        # Process uploaded file
        raw_text = await process_file(cv)
        
        # Analyze criteria
        analysis = analyze_criteria(raw_text)
        
        # Format results
        criteria_results = [
            CriterionResult(
                criterion=criterion,
                evidence=evidence,
                satisfied=len(evidence) > 0
            )
            for criterion, evidence in analysis.items()
        ]
        
        # Calculate rating
        rating = calculate_rating(analysis)
        
        return VisaAssessment(criteria=criteria_results, rating=rating)
        
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
