from transformers import pipeline

intents = [
  "CREDIT_CARD_DISCUSSION",
  "UNSECURED_LOAN_DISCUSSION",
  "SECURED_LOAN_DISCUSSION",
  "SAVINGS_DISCUSSION",
  "INSURANCE_DISCUSSION",
  "DIGITAL_BANKING_DISCUSSION",
  "BANK_ACCOUNT_DISCUSSION",
  "LOAN_REPAYMENT_DISCUSSION",
  "PRODUCT_COMPARISON",
  "GENERAL_INQUIRIES",
  "INTEREST_RATE_INQUIRY",
  "DOCUMENT_REQUIREMENTS",
  "PROMOTIONS_AND_OFFERS",
  "CUSTOMER_SUPPORT_REQUEST",
  "MOBILE_APP_INQUIRY",
  "REPAYMENT_SCHEDULE"
]

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
def classify_intent(text: str):
    result = classifier(text, candidate_labels=intents)
    return {
        "label": result["labels"][0],
        "score": result["scores"][0]
    }