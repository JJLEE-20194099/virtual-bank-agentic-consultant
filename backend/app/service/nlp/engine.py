from app.service.sentiment.engine import analyze_sentiment
def analyze(text: str):
    
    """
    I implemented naive method to test pipeline
    """
    
    intents = []
    entities = []

    t = text.lower()

    if "invest" in t or "investment" in t:
        intents.append("INVESTMENT_DISCUSSION")

    if "mortgage" in t or "loan" in t:
        intents.append("CREDIT_DISCUSSION")

    if "real estate" in t:
        entities.append({
            "type": "ASSET_CLASS",
            "value": "REAL_ESTATE"
        })
        
    sentiment_result = analyze_sentiment(text)

    return {
        "transcript": text,
        "sentiment_result":sentiment_result,
        "intents": intents,
        "entities": entities,
        "risk_keywords": ["invest", "return"] if intents else []
    }
