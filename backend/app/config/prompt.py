ADVISE_BASED_ON_CONVERSATION_CLIENT_PROMPT = """You are a financial advisory assistant.

Based on the following conversation between a financial advisor and a client, generate exactly 3 short and specific recommendations (maximum 150 characters each) for the advisor.

Focus on:
- Client life events or concerns mentioned in the conversation
- Portfolio adjustments
- Concrete follow-up actions

Conversation transcript:
{conversation_data}

Client information (background data, if needed):
{client_data}

Output format (exactly):
- [Client Name] mentioned [life event or concern]. Advisor should [specific action].

Rules:
- Exactly 3 recommendations
- Max 150 characters per recommendation
- One sentence per recommendation
- No generic advice
- No extra text outside the list
"""