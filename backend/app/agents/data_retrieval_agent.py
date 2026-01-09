from app.agents.baseline_agent import BaselineAgent
from config.prompt import CLIENT_EXTRACT_PROMPT

class DataRetrievalAgent(BaselineAgent):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def load_data():
        pass
    
    def extract_data_by_query(self, data_obj, query_type, query):
        prompt = CLIENT_EXTRACT_PROMPT.format(
            query = query, data = data_obj
        )
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are an information extraction assistant specializing in financial {query_type} data. "
                    "Your task is to extract and summarize only information that is explicitly relevant "
                    "to the given query, without making assumptions or adding new details."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        response = self.get_completion(messages, temperature=0.25)
        
        return response
