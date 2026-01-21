import os
from app.agents.baseline_agent import BaselineAgent
from app.config.prompt import QUERY_EXTRACT_PROMPT
from app.config.query import CLIENT_INFO_QUERY, CLIENT_COLLECTION

class SaleAgent(BaselineAgent):
    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
    
    def extract_response_based_on_query(self, query, bank_services, client_data, qa_data):
        prompt = QUERY_EXTRACT_PROMPT.format(
            query=query,
            bank_services=bank_services,
            client_data=client_data,
            qa_data=qa_data,
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a financial assistant. Your task is to identify and provide specific responses or actions based on available bank services "
                    "and frequently asked questions (QA)."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        response = self.get_completion(messages, temperature=0.25)
        return response.strip()

    def run(self, customer_data, query, qa_data, bank_services):
        response = self.extract_response_based_on_query(
            query=query, 
            bank_services=bank_services, 
            client_data=customer_data, 
            qa_data=qa_data
        )
        
        return response
