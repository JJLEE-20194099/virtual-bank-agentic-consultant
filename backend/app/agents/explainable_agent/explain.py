from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain(feature, behaviors):
    prompt = f"""
    User financial summary:
    - Total spend: {feature['total_spend']}
    - Travel ratio: {feature['travel_ratio']}
    - Installment ratio: {feature['installment_ratio']}
    Behaviors detected: {behaviors}

    Explain in Vietnamese, friendly tone, no financial advice.
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content
