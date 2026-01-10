from transformers import pipeline

sentiment = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    r = sentiment(text)[0]
    return {
        "label": r["label"],
        "score": r["score"]
    }
    