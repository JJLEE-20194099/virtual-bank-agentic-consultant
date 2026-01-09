import random
import json
from faker import Faker

fake = Faker("vi_VN")

def generate_customer(customer_id):
    age = random.randint(22, 60)
    gender = random.choice(["Male", "Female"])
    marital_status = random.choice(["Single", "Married"])
    dependents = random.randint(0, 3) if marital_status == "Married" else 0
    location = random.choice(["Ho Chi Minh City", "Hanoi", "Da Nang", "Hai Phong"])
    education_level = random.choice(["High School", "Bachelor", "Master", "Doctorate"])
    occupation = random.choice([
        "Software Engineer", "Sales Manager", "Teacher", "Accountant",
        "Doctor", "Marketing Specialist", "Business Owner", "AI Engineer",
    ])

    monthly_income_vnd = random.randint(15000000, 100000000) 
    income_type = "Salary"
    employment_type = "Full-time"
    years_of_experience = random.randint(1, 30)

    spending_level = random.choice(["Low", "Medium", "Medium-High", "High"])
    saving_habit = random.choice(["Occasional", "Regular", "Active"])
    risk_appetite = random.choice(["Low", "Medium", "High"])

    credit_score = random.randint(600, 750)
    total_active_loans = random.randint(0, 3)
    total_outstanding_debt_vnd = random.randint(0, 2000000000)  

    loan_types = ["Home Loan", "Personal Loan", "Auto Loan"]
    banks = ["Vietcombank", "Techcombank", "MB Bank", "VPBank", "VIB", "Sacombank"]

    loan_records = []
    for i in range(total_active_loans):
        original_amount = random.randint(100000000, 1500000000)
        outstanding_amount = random.randint(0, original_amount)
        loan = {
            "loan_id": f"VN_LOAN_{customer_id}_{i+1}",
            "loan_type": random.choice(loan_types),
            "bank": random.choice(banks),
            "original_amount_vnd": original_amount,
            "outstanding_amount_vnd": outstanding_amount,
            "interest_rate_percent": round(random.uniform(7.0, 15.0), 1),
            "tenure_months": random.choice([12, 24, 36, 60, 120, 240]),
            "start_date": str(fake.date_between(start_date="-5y", end_date="today")),
            "repayment_status": random.choice(["On-time", "Late", "New"]),
            "late_payment_count": random.randint(0, 3)
        }
        loan_records.append(loan)
    
    repaid_loans = []
    for i in range(random.randint(0, 3)):  
        original_amount = random.randint(10000000, 1000000000)
        tenure = random.choice([12, 24, 36, 60, 120])
        start_date = fake.date_between(start_date="-10y", end_date="-1y")
        end_date = fake.date_between(start_date=start_date, end_date="-1y")
        loan = {
            "loan_id": f"VN_REPAID_{customer_id}_{i+1}",
            "loan_type": random.choice(loan_types),
            "bank": random.choice(banks),
            "original_amount_vnd": original_amount,
            "interest_rate_percent": round(random.uniform(7.0, 15.0), 1),
            "tenure_months": tenure,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "repayment_status": "Repaid",
            "late_payment_count": random.randint(0, 2)
        }
        repaid_loans.append(loan)

    card_types = ["Credit Card", "Debit Card"]
    card_records = []
    for j in range(random.randint(0, 2)):
        card = {
            "card_id": f"VN_CARD_{customer_id}_{j+1}",
            "card_type": "Credit Card",
            "bank": random.choice(banks),
            "credit_limit_vnd": random.randint(5000000, 200000000),
            "annual_fee_vnd": random.randint(100000, 2000000),
            "benefits": random.sample(["Cashback", "Air Miles", "Travel Lounge", "E-commerce Discount", "Dining Discount"], k=2),
            "monthly_spend_avg_vnd": random.randint(1000000, 20000000),
            "usage_pattern": random.choice(["Online shopping", "Travel & dining", "Utilities & bills", "General spending"])
        }
        card_records.append(card)

    customer = {
        "customer_id": f"VN_CUST_{customer_id}",
        "personal_info": {
            "name": fake.name(),
            "age": age,
            "gender": gender,
            "marital_status": marital_status,
            "dependents": dependents,
            "location": location,
            "education_level": education_level,
            "occupation": occupation
        },
        "income_profile": {
            "monthly_income_vnd": monthly_income_vnd,
            "income_type": income_type,
            "employment_type": employment_type,
            "years_of_experience": years_of_experience
        },
        "financial_behavior": {
            "spending_level": spending_level,
            "saving_habit": saving_habit,
            "risk_appetite": risk_appetite
        },
        "credit_history": {
            "credit_score": credit_score,
            "total_active_loans": total_active_loans,
            "total_outstanding_debt_vnd": total_outstanding_debt_vnd,
            "loan_records": loan_records,
            "repaid_loans": repaid_loans,
            "credit_card_records": card_records
        }
    }

    return customer

mock_customers = [generate_customer(i+1) for i in range(100)]

with open("backend/app/data/clients.json", "w", encoding="utf-8") as f:
    json.dump(mock_customers, f, ensure_ascii=False, indent=2)
