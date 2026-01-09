from app.agents.baseline_agent import BaselineAgent
from config.prompt import CLIENT_EXTRACT_PROMPT, CLIENT_TRANSCRIPT_EXTRACT_PROMPT
import json

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
    
    def extract_client_info_by_transcript(transcript):
        prompt = CLIENT_TRANSCRIPT_EXTRACT_PROMPT.format(transcript=transcript),
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict information extraction and validation engine. "
                    "Extract only client facts that are explicitly stated in the conversation. "
                    "Do not infer, assume, normalize, or add missing information. "
                    "Return valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": prompt
            },
        ]

        response = self.get_completion(messages, temperature=0, response_format={"type": "json_object"})
        
        return json.loads(response)
        
