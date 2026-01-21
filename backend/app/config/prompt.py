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

CLIENT_EXTRACT_PROMPT = """
You are an information extraction assistant.

Given a structured client data object, extract and summarize ONLY the information that is directly relevant to the following query:

Query:
{query}

Client data:
{data}

Instructions:
- Use only information explicitly present in the client data
- Do not infer or assume missing details
- Ignore irrelevant fields
- Keep the summary concise and focused on the query
- If no relevant information exists, return: "No relevant information found."

Output:
A short, clear summary in plain text.
"""


CLIENT_TRANSCRIPT_EXTRACT_PROMPT = """You are an information extraction assistant.

Your task is to extract ONLY factual information about the client that is explicitly stated in the conversation below.

Rules:
- Use ONLY information that is directly stated in the conversation
- Do NOT infer, assume, or guess
- Do NOT normalize or reinterpret the information
- If a fact is not explicitly mentioned, do NOT include it
- Output MUST be valid JSON
- Include ONLY fields that are explicitly mentioned

Conversation transcript:
{transcript}

Return a JSON object using ONLY the following allowed fields:
{
  "Location": "client's explicitly stated location",
  "Marital Status": "client's explicitly stated marital status",
  "Number of Children": "explicitly stated number of children",
  "Occupation": "explicitly stated occupation",
  "Educational Level": "explicitly stated educational level",
  "Address": "explicitly stated address"
}

"""

QUERY_EXTRACT_PROMPT = """
You are a financial assistant. Given the client's query, identify and provide specific responses or actions based on available bank services and frequently asked questions (QA).

Query:
{query}

Bank services and products:
{bank_services}

Client information:
{client_data}

Frequently Asked Questions (QA):
{qa_data}

Instructions:
- Match the query with the relevant bank service or product.
- Check the QA list for common questions related to the client's query.
- Suggest a solution or next action for the client based on the information provided.
- If the query is about an unsecured loan, suggest actions based on the bank's unsecured loan products.
- If a matching QA exists, provide a relevant response or follow-up action based on the QA.

Output:
A specific, actionable response to the client query based on bank offerings and frequently asked questions.
"""
