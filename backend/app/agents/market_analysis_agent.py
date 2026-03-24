import os
from app.agents.baseline_agent import BaselineAgent
from app.config.prompt import MARKET_ANALYSIS_PROMPT, MARKET_ANALYSIS_RESPONSE_FORMAT, STOCK_PRODUCT_RECOMMENDATION_PROMPT, STOCK_ANALYSIS_PROMPT
import json 
import re

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

        full_text = ""

        for chunk in self.get_completion(messages, temperature=0.25):
            full_text += chunk
            yield chunk + " "
        # return {
        #     "query_parser": query_parser,
        #     "ohlcv_data": ohlcv_data,
        #     "answer": answer
        # }

    
    def recommend_stock_product(self, user_context_data, features, pre_products):

        prompt = STOCK_PRODUCT_RECOMMENDATION_PROMPT.replace(
            "{user_context_data}",
            json.dumps(user_context_data, ensure_ascii=False)
        ).replace(
            "{features}",
            json.dumps(features, ensure_ascii=False)
        ).replace(
            "{pre_products}",
            json.dumps(pre_products, ensure_ascii=False)
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là chuyên gia tư vấn đầu tư tại công ty chứng khoán/ngân hàng.\n\n"

                    "MỤC TIÊU:\n"
                    "- Tối ưu lợi nhuận & giảm rủi ro cho khách hàng\n"
                    "- Đồng thời tối đa hóa doanh thu từ sản phẩm tài chính\n\n"

                    "QUY TẮC BẮT BUỘC:\n"
                    "- Luôn trả lời bằng tiếng Việt\n"
                    "- CHỈ trả về JSON hợp lệ (không thêm text ngoài JSON)\n"
                    "- Phải đề xuất >= 5 sản phẩm\n"
                    "- Phải sử dụng phần lớn sản phẩm từ pre_products\n"
                    "- Reason phải bám sát insights (cash, risk, loss, market...)\n\n"

                    "ƯU TIÊN QUYẾT ĐỊNH:\n"
                    "- Market risk cao → ưu tiên giảm rủi ro\n"
                    "- Có lỗ → STOP LOSS / REBALANCE\n"
                    "- Cash cao → CASH PRODUCTS\n"
                    "- Cash thấp → MARGIN / CREDIT\n"
                    "- Portfolio lớn → VIP / WEALTH\n\n"

                    "ƯU TIÊN DOANH THU:\n"
                    "1. Margin / Loan\n"
                    "2. Derivatives\n"
                    "3. Advisory / Wealth\n"
                    "4. Cash products\n\n"

                    "FORMAT OUTPUT (BẮT BUỘC):\n"
                    "{\n"
                    "  \"type\": \"MULTI_PRODUCT\",\n"
                    "  \"title\": \"...\",\n"
                    "  \"summary\": \"...\",\n"
                    "  \"products\": [\n"
                    "    {\n"
                    "      \"name\": \"...\",\n"
                    "      \"group\": \"TRADING | PORTFOLIO | CASH | LOAN | RISK | VIP\",\n"
                    "      \"priority\": 1,\n"
                    "      \"description\": \"...\",\n"
                    "      \"reason\": \"...\",\n"
                    "      \"expected_benefit\": \"...\",\n"
                    "      \"revenue_driver\": \"...\"\n"
                    "    }\n"
                    "  ],\n"
                    "  \"confidence_score\": \"low | medium | high\"\n"
                    "}\n"
                )
            },
            {
                "role": "user",
                "content": prompt  
            }
        ]

        answer = self.get_completion(messages, temperature=0.25)
        

        answer = re.sub(r"```json|```", "", answer).strip()
        answer = json.loads(answer)
        return {
            "answer": answer
        }

    def analyze_stock_portfolio(self, user_portfolio_data):

        prompt = STOCK_ANALYSIS_PROMPT.replace(
            "{user_portfolio_data}",
            json.dumps(user_portfolio_data, ensure_ascii=False, default=str)
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là chuyên gia phân tích cổ phiếu tại công ty chứng khoán.\n\n"

                    "MỤC TIÊU:\n"
                    "- Phân tích từng mã cổ phiếu trong danh mục\n"
                    "- Đưa ra nhận định rõ ràng về xu hướng, rủi ro và vị trí trong portfolio\n"
                    "- Đưa ra lời khuyên với cổ phiếu đó, có thể xem các thông tin về công ty đó để đưa ra lời khuyên cùng với xu hướng\n\n"

                    "QUY TẮC BẮT BUỘC:\n"
                    "- Luôn trả lời bằng tiếng Việt\n"
                    "- CHỈ trả về JSON hợp lệ (không text ngoài JSON)\n"
                    "- Phải phân tích TẤT CẢ các mã trong danh mục\n"
                    "- Không được bỏ sót cổ phiếu nào\n"
                    "- Phân tích phải dựa trên dữ liệu thực tế (trend, volatility, PnL, sector, weight)\n\n"

                    "TIÊU CHÍ PHÂN TÍCH:\n"
                    "- Xu hướng (bullish / bearish / downtrend / uptrend)\n"
                    "- Rủi ro (volatility + risk score)\n"
                    "- Vai trò trong danh mục (core / satellite / overweight)\n"
                    "- Tỷ trọng danh mục (portfolio_pct)\n"
                    "- Lãi/lỗ chưa thực hiện\n"
                    "- Tính tập trung rủi ro\n\n"

                    "FORMAT OUTPUT (BẮT BUỘC):\n"
                    "{\n"
                    "  \"MÃ_CỔ_PHIẾU\": {\n"
                    "    \"stock_analysis\": \"Phân tích ngắn gọn về xu hướng, rủi ro, vai trò trong danh mục\",\n"
                    "    \"stock_advice\": \"Đưa ra những ý kiến về mã cổ phiếu này ở các khía cạnh: công ty, trend, category,...\"\n"
                    "  }\n"
                    "}\n"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        answer = self.get_completion(messages, temperature=0.2)

        answer = re.sub(r"```json|```", "", answer).strip()

        try:
            answer = json.loads(answer)
        except Exception as e:
            return {
                "error": "Invalid JSON from model",
                "raw_output": answer
            }

        return {
            "answer": answer
        }

