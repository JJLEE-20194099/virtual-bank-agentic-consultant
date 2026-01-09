import os
from app.agents.baseline_agent import BaselineAgent
from app.agents.data_retrieval_agent import DataRetrievalAgent
from config.prompt import ADVISE_BASED_ON_CONVERSATION_CLIENT_PROMPT
from config.query import CLIENT_INFO_QUERY, CLIENT_COLLECTION

class FinancialConsultingAgent(BaselineAgent):
    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
    
    def advise_based_on_conversation_and_client(self, conversation_data, client_data):
        prompt = ADVISE_BASED_ON_CONVERSATION_CLIENT_PROMPT.format(
            conversation_data = conversation_data, client_data = client_data, 
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a financial advisory assistant. "
                    "Your task is to generate concise, specific, and actionable recommendations "
                    "based strictly on the provided conversation."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        response = self.get_completion(messages, temperature=0.25)
        advise_list = [
            item.strip() for item in response.split("\n")
        ]
        return advise_list

    def run(self, conversation_data, client_obj):
        data_retrieval_agent = DataRetrievalAgent()
        client_data = data_retrieval_agent.extract_data_by_query(
            data = client_obj,
            query_type = CLIENT_COLLECTION,
            query = CLIENT_INFO_QUERY
        )
        
        advise_list = self.advise_based_on_conversation_and_client(
            conversation_data = conversation_data, 
            client_data = client_data["summary"] if isinstance(client_data, dict) else client_data,
        )
        
        return advise_list

        


