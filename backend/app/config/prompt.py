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


MARKET_ANALYSIS_PROMPT = """
Bạn là hệ thống phân tích câu hỏi tài chính nâng cao.

Nhiệm vụ:
1. Xác định intent
2. Trích xuất mã cổ phiếu (symbols)
3. Xác định external factors
4. Xác định có cần dữ liệu company_info hay không
5. Trả về JSON chuẩn

---

## Intent:
- "compare": so sánh cổ phiếu
- "price": hỏi giá
- "analysis": phân tích
- "buy_sell": hỏi mua/bán
- "portfolio": danh mục
- "trend": xu hướng
- "volatility": biến động
- "news": tin tức
- "impact": yếu tố ảnh hưởng (macro → stock)
- "company_info": hỏi thông tin doanh nghiệp
- "general": chung chung
- "unknown": không xác định

---
## External factors:

Trích xuất các yếu tố bên ngoài ảnh hưởng tới cổ phiếu.

Mỗi yếu tố có cấu trúc:

{
  "type": "...",
  "scope": "...",
}

---

### type:
- "exchange_rate" → tỷ giá, USD, forex
- "gold" → vàng
- "oil" → dầu
- "interest_rate" → lãi suất
- "company_info" → khi câu hỏi liên quan nội tại doanh nghiệp

---

### scope:
- "domestic": trong nước (Việt Nam)
- "global": thế giới
- KHÔNG áp dụng cho "company_info"

---

### sub_type (nếu có):
- gold:
  - "sjc", "9999" → domestic
  - "spot" → global

- oil:
  - "brent", "wti" → global

- exchange_rate:
  - "usd_vnd" → domestic
  - "dxy" → global

- interest_rate:
  - "sbv" (Việt Nam)
  - "fed" (Mỹ)

- macro_index:
  - "vnindex"
  - "sp500"

- crypto:
  - "btc", "eth"

---

## Quy tắc:
- Symbol là chữ IN HOA (FPT, VNM, AAPL…)
- Chuẩn hóa về uppercase
- Không đoán nếu không chắc chắn
- External factor chỉ extract nếu có rõ ràng
- Nếu không rõ phạm vi → scope = "unknown"
- company_info → không có scope
---

## Ví dụ:

Input: "Giá vàng SJC có ảnh hưởng tới FPT không?"
Output:
{
  "intent": "impact",
  "symbols": ["FPT"],
  "external_factors": [
    {
      "type": "gold",
      "scope": "domestic",
      "sub_type": "sjc",
    }
  ],
  "requires_company_data": false,
  "confidence": 0.95
}

Input: "Lãi suất ảnh hưởng tới VNM thế nào?"
Output:
{
  "intent": "impact",
  "symbols": ["VNM"],
  "external_factors": [
    {
      "type": "interest_rate",
      "scope": "domestic",
      
    }
  ],
  "requires_company_data": false,
  "confidence": 0.94
}

Input:"FPT hoạt động kinh doanh ra sao?"
Output:
{
  "intent": "company_info",
  "symbols": ["FPT"],
  "external_factors": [
    {
      "type": "company_info",
    }
  ],
  "requires_company_data": true,
  "confidence": 0.96
}

Input:"So sánh FPT và VNM"
Output:
{
  "intent": "compare",
  "symbols": ["FPT", "VNM"],
  "external_factors": [],
  "requires_company_data": false,
  "confidence": 0.97
}

Input:"USD ảnh hưởng gì tới cổ phiếu FPT?"
Output:
{
  "intent": "impact",
  "symbols": ["FPT"],
  "external_factors": [
    {
      "type": "exchange_rate",
      "scope": "domestic",
    }
  ],
  "requires_company_data": false,
  "confidence": 0.95
}


Input:"Giá vàng thế giới ảnh hưởng FPT?"
Output:
{
  "intent": "impact",
  "symbols": ["FPT"],
  "external_factors": [
    {
      "type": "gold",
      "scope": "global",
    }
  ],
  "requires_company_data": false,
  "confidence": 0.96
}

Input:"FPT làm gì?"
Output:
{
  "intent": "company_info",
  "symbols": ["FPT"],
  "external_factors": [
    {
      "type": "company_info",
    }
  ],
  "requires_company_data": true,
  "confidence": 0.97
}

Input: Giá vàng thế giới giảm có ảnh hưởng đến giá vàng trong nước hôm nay không
{
  "intent": "impact",
  "symbols": [],
  "external_factors": [
    {
      "type": "gold",
      "scope": "global"
    },
    {
      "type": "gold",
      "scope": "domestic"
    }
  ],
  "requires_company_data": false,
  "confidence": 0.93
}

Câu người dùng:
"{message}"

Trả về JSON:
"""

