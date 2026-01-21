from app.service.sentiment.engine import analyze_sentiment
from app.service.intent.engine import classify_intent
from app.service.ner.engine import detect_entity
def analyze(text: str):
    
    """
    I implemented naive method to test pipeline
    """
    
    intents = []
    entities = []

    t = text.lower()
        
    sentiment_result = analyze_sentiment(text)
    intent_result = classify_intent(text)
    entities_result = detect_entity(text)

    return {
        "transcript": text,
        "sentiments":sentiment_result,
        "intents":intent_result,
        "entities":entities_result,
        "risk_keywords": []
    }
