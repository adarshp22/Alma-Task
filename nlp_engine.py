nlp = spacy.load("en_core_web_lg")

def analyze_criteria(text: str) -> dict:
    """Identifies O1A criteria matches"""
    doc = nlp(text)
    
    results = {
        "awards": [],
        "memberships": [],
        # ... other criteria
    }
    
    # Custom entity matching
    for ent in doc.ents:
        if ent.label_ == "ORG":
            if is_elite_org(ent.text):
                results["memberships"].append(ent.text)
    
    # Pattern matching for awards
    matcher = spacy.matcher.Matcher(nlp.vocab)
    matcher.add("AWARD", [[
        {"LOWER": {"IN": ["award", "prize"]}},
        {"ENT_TYPE": "ORG"}
    ]])
    
    for match_id, start, end in matcher(doc):
        results["awards"].append(doc[start:end].text)
    
    return results
