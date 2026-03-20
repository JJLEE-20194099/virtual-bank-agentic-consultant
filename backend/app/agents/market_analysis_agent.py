import os
from app.agents.baseline_agent import BaselineAgent
from config.prompt import MARKET_ANALYSIS_PROMPT

class MarketAnalysisAgent(BaselineAgent):
    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
    
    def analyse_market_question(self, user_question):
        prompt = MARKET_ANALYSIS_PROMPT.format(
            message = user_question
        )

        messages = [
            {
                "role": "system",
                "content": (
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
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        query_parser = self.get_completion(messages, temperature=0.25)
        print(query_parser)
        return query_parser

    def run(self, user_question):
        
        query_parser = self.advise_based_on_conversation_and_client(
            user_question
        )
        
        return query_parser

        


