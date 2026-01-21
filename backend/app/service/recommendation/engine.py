from app.service.recommendation.products import PRODUCTS
import json
from app.agents.sale_agent import SaleAgent

with open('app/data/intents.json', 'r') as file:
    qa_data = json.load(file)
    
with open('app/data/products.json', 'r') as file:
    bank_services = json.load(file)

def recommend(nlp, compliance_issue, customer_data):
    customer_data = {
        "customer_id": "VN_CUST_10",
        "personal_info": {
            "name": "Quý ông Trọng Đặng",
            "age": 56,
            "gender": "Male",
            "marital_status": "Married",
            "dependents": 2,
            "location": "Da Nang",
            "education_level": "High School",
            "occupation": "Doctor"
        },
        "income_profile": {
            "monthly_income_vnd": 54775910,
            "income_type": "Salary",
            "employment_type": "Full-time",
            "years_of_experience": 11
        },
        "financial_behavior": {
            "spending_level": "High",
            "saving_habit": "Regular",
            "risk_appetite": "High"
        },
        "credit_history": {
            "credit_score": 656,
            "total_active_loans": 3,
            "total_outstanding_debt_vnd": 349971357,
            "loan_records": [
                {
                    "loan_id": "VN_LOAN_10_1",
                    "loan_type": "Personal Loan",
                    "bank": "Techcombank",
                    "original_amount_vnd": 209357103,
                    "outstanding_amount_vnd": 184388823,
                    "interest_rate_percent": 14.8,
                    "tenure_months": 240,
                    "start_date": "2022-04-11",
                    "repayment_status": "On-time",
                    "late_payment_count": 0
                },
                {
                    "loan_id": "VN_LOAN_10_2",
                    "loan_type": "Auto Loan",
                    "bank": "MB Bank",
                    "original_amount_vnd": 653707597,
                    "outstanding_amount_vnd": 94765958,
                    "interest_rate_percent": 12.4,
                    "tenure_months": 12,
                    "start_date": "2025-08-12",
                    "repayment_status": "On-time",
                    "late_payment_count": 3
                },
                {
                    "loan_id": "VN_LOAN_10_3",
                    "loan_type": "Auto Loan",
                    "bank": "VIB",
                    "original_amount_vnd": 965927594,
                    "outstanding_amount_vnd": 211362558,
                    "interest_rate_percent": 8.3,
                    "tenure_months": 12,
                    "start_date": "2023-03-14",
                    "repayment_status": "On-time",
                    "late_payment_count": 0
                }
            ],
            "repaid_loans": [],
            "credit_card_records": [
                {
                    "card_id": "VN_CARD_10_1",
                    "card_type": "Credit Card",
                    "bank": "Vietcombank",
                    "credit_limit_vnd": 147339536,
                    "annual_fee_vnd": 899138,
                    "benefits": [
                    "Air Miles",
                    "Cashback"
                    ],
                    "monthly_spend_avg_vnd": 4261595,
                    "usage_pattern": "Utilities & bills"
                }
            ]
        }
    }
    
    recommendations = SaleAgent().run(
        customer_data = customer_data, 
        query = nlp["transcript"], 
        qa_data = qa_data, 
        bank_services = bank_services
    )

    return recommendations
