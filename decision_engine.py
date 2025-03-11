CRITERIA_WEIGHTS = {
    "awards": 0.25,
    "original_contribution": 0.20,
    "scholarly_articles": 0.15,
    "high_remuneration": 0.15,
    "membership": 0.10,
    "press": 0.07,
    "judging": 0.05,
    "critical_employment": 0.03
}

def calculate_rating(analysis: dict) -> str:
    """Converts analysis results to qualification rating"""
    score = sum(
        CRITERIA_WEIGHTS[criterion] * len(evidence)
        for criterion, evidence in analysis.items()
    )
    
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"
