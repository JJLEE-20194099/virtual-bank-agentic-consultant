import os
from app.agents.baseline_agent import BaselineAgent
from app.config.prompt import MARKET_ANALYSIS_PROMPT, MARKET_ANALYSIS_RESPONSE_FORMAT

class MarketAnalysisAgent(BaselineAgent):
    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
    
    def analyse_market_question(self, user_question):

        prompt = MARKET_ANALYSIS_PROMPT.replace("{message}", user_question)
        messages = [
            {
                "role": "system",
                "content": """
                    "You are a financial query parser.\n"
                    "Your task is to analyze a user's message and extract structured information.\n\n"
                    
                    "You must:\n"
                    "1. Identify the user intent\n"
                    "2. Extract stock symbols (uppercase)\n"
                    "3. Detect external factors (exchange_rate, gold, oil, interest_rate, company_info)\n"
                    "4. Determine if company data is required\n"
                    "5. Return ONLY valid JSON (no explanation)\n\n"
                    
                    "Intent types:\n"
                    "- compare\n"
                    "- price\n"
                    "- analysis\n"
                    "- buy_sell\n"
                    "- portfolio\n"
                    "- news\n"
                    "- impact\n"
                    "- company_info\n"
                    "- general\n"
                    "- unknown\n\n"
                    
                    "Rules:\n"
                    "- Symbols must be uppercase (e.g., FPT, VNM, AAPL)\n"
                    "- Do NOT guess symbols if uncertain\n"
                    "- Only extract external factors if clearly mentioned\n"
                    "- 'company_info' should be used when the query is about internal company data\n\n"
                    
                    "Output format:\n"
                    "{\n"
                    '  "intent": "...",\n'
                    '  "symbols": [],\n'
                    '  "external_factors": [],\n'
                    '  "requires_company_data": true/false,\n'
                    '  "confidence": 0.0\n'
                    "}"
                """,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        query_parser = self.get_completion(messages, temperature=0.25)
        return query_parser

    def run(self, user_question):
        
        query_parser = self.advise_based_on_conversation_and_client(
            user_question
        )
        
        return query_parser

        
    def response_market_question(self, context, user_question, query_parser):
        
        intent = query_parser["intent"]
        symbols = query_parser["symbols"]
        company_info = context.get("company_info", {})
        ohlcv_data = context.get("ohlcv", {})
        exchange_rate = context.get("exchange_rate", "N/A")

        prompt = MARKET_ANALYSIS_RESPONSE_FORMAT.format(
            intent=intent,
            symbols=symbols,
            company_info=company_info,
            ohlcv_data=ohlcv_data,
            user_message=user_question,
            exchange_rate=exchange_rate
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là chuyên gia phân tích tài chính.\n"
                    "Nhiệm vụ của bạn:\n"
                    "1. Trả lời câu hỏi của người dùng dựa trên dữ liệu đã có.\n"
                    "2. Chỉ dùng dữ liệu từ context (OHLCV, company_info, giá vàng, dầu, tỷ giá…)\n"
                    "3. Trình bày câu trả lời dễ hiểu, có số liệu minh họa nếu có.\n"
                    "4. Không dự đoán nếu không có dữ liệu.\n\n"
                    "Intent có thể là:\n"
                    "- compare, price, analysis, buy_sell, portfolio, news, impact, company_info, general, unknown\n\n"
                    "Yêu cầu:\n"
                    "- Nếu intent là 'price', trả lời liên quan đến giá.\n"
                    "- Nếu intent là 'analysis', đưa phân tích ngắn hạn dựa trên OHLCV.\n"
                    "- Nếu intent là 'impact', phân tích ảnh hưởng của các yếu tố bên ngoài.\n"
                    "- Nếu intent là 'company_info', tóm tắt và phân tích thông tin doanh nghiệp.\n"
                    "- Nếu intent là 'compare', so sánh các cổ phiếu dựa trên dữ liệu có sẵn.\n"
                    "- Trình bày dễ hiểu, có thể kèm số liệu.\n"
                )
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        answer = self.get_completion(messages, temperature=0.25)
        return {
            "query_parser": query_parser,
            "ohlcv_data": ohlcv_data,
            "answer": answer
        }