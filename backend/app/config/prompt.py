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
-- Nếu intent khác → đưa thông tin tổng quan, giải thích đơn giản.
- External factor chỉ extract nếu có rõ ràng
- Nếu không rõ phạm vi → scope = "unknown"
- company_info → không có scope
- (Có giá xăng trong nước trong thông tin giá dầu). Nên khi hỏi về giá dầu cx đồng nghĩa hãy trả lời và lấy dữ liệu giá xăng nữa.
- Nếu hỏi mua bán vàng thì external factors vẫn là gold.
- Khi hỏi mua bán cổ phiếu thì hãy luôn có yêu cầu thông tin công ty vì điều đó giúp cho việc người dùng hiểu hơn về công ty phát hành cổ phiếu đó, tức là company_info nằm trong external factors
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

Câu hỏi của người dùng:
"{message}"

Trả về JSON:
"""


MARKET_ANALYSIS_RESPONSE_FORMAT = """
Bạn là chuyên gia phân tích tài chính. Dựa trên dữ liệu đã được trích xuất, hãy cung cấp thông tin chính xác, ngắn gọn và dựa trên dữ liệu thực tế.  

## Dữ liệu hiện có:

- Intent: {intent}
- Symbols: {symbols}
- OHLCV và các chỉ số liên quan (Giá của cổ phiếu, giá vàng hoặc giá dầu trong và ngoài nước): {ohlcv_data}
- Company info (nếu có): {company_info}
- External factors (Các yếu tố bên ngoài ảnh hưởng tới cổ phiếu): {exchange_rate}

## Hướng dẫn trả lời:
1. Nếu intent là "price" → cung cấp giá hiện tại hoặc giá gần nhất.  
2. Nếu intent là "analysis" → trình bày phân tích ngắn hạn (7 ngày) dựa trên OHLCV, chỉ số biến động, thanh khoản.  
3. Nếu intent là "impact" → mô tả tác động của các yếu tố bên ngoài tới cổ phiếu.  
4. Nếu intent là "company_info" → cung cấp thông tin hoạt động, sản phẩm, chiến lược của công ty.  
5. Nếu intent là "compare" → trình bày so sánh trực tiếp giữa các cổ phiếu dựa trên dữ liệu có sẵn (giá, biến động, thanh khoản).  
6. Nếu intent là "buy_sell" → dựa trên phân tích dữ liệu (OHLCV), tính toán trend xu hướng và đưa ra gợi ý mua/bán nhưng không được mang tính chủ quan, chỉ dựa trên dữ liệu.
7. Nếu intent là unknown / khác → đưa thông tin tổng quan, dữ liệu thực tế, tránh đánh giá chủ quan.  

- Chỉ sử dụng dữ liệu có sẵn trong `context`.  
- Không đưa ra dự đoán nếu dữ liệu không có.  
- Trình bày dễ hiểu, kèm số liệu cụ thể khi có.

### Ví dụ trả lời:
- FPT hiện có giá đóng cửa trung bình 7 ngày là 40.000 VND/cổ phiếu, dao động ±2%.  
- Giá vàng thế giới tăng có thể khiến giá vàng trong nước tăng nhẹ.  
- VNM hiện kinh doanh trong lĩnh vực sữa, thực phẩm, lợi nhuận ổn định 6 tháng gần nhất.

Câu hỏi của người dùng: {user_message}

Trả lời:
"""