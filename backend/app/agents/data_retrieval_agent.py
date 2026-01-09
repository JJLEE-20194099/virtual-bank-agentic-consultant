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
    
    def validate_client_data(self, storage_client_data, extract_client_data) -> list:
       
        validation_results = []
        

        for extracted_key, extracted_client_value in extract_client_data.items():
            if extracted_key in storage_client_data:
                client_state_value = storage_client_data[extracted_key]
                if extracted_client_value != client_state_value:
                    validation_results.append(
                        {
                            "transcript_key": extracted_key,
                            "transcript_value": extracted_client_value,
                            "client_state_key": extracted_key,
                            "client_state_value": client_state_value,
                        }
                    )

        return validation_results
    
    def generate_client_validate_report(self, storage_client_data, extract_client_data):
      
        validation_results = self.validate_client_data(storage_client_data, extract_client_data)

        findings = []
        for result in validation_results:
            finding = f"- Based on transcript, client mentioned {result['transcript_key'].lower()} ({result['transcript_value']}). The agent checked the client database noting {result['client_state_key'].lower()} is {result['client_state_value']}."
            findings.append(finding)

        if not findings:
            findings.append("No data inconsistencies or quality concerns were found in the conversation")

        return findings
    
    def run(self, storage_client_data, extract_client_data):
        return self.generate_client_validate_report(storage_client_data, extract_client_data)
        
