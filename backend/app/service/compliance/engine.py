from app.service.compliance.rules import check_suitability, check_disclosure

def run_compliance(nlp, customer):
    issues = []
    
    transcript = nlp.get("transcript", "")
    issues += check_suitability(nlp, customer)
    issues += check_disclosure(nlp, transcript)
    return issues
