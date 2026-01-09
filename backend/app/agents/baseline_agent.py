import openai
from dotenv import load_dotenv
import os
from config.index import LLM_MODEL_NAME, OPENAI_API_KEY
from processor.chat import ChatProcessor

class BaselineAgent:

    def __init__(self, model_name = LLM_MODEL_NAME, temperature = 0.1):
        self.model_name = model_name
        self.temperature = temperature

    def run(self, *args, **kwargs):
        raise NotImplementedError("'run' method has been install in subclass")
    def get_completion(self, messages, temperature = None, response_format = None):
        chat_processor = ChatProcessor(
            api_key=OPENAI_API_KEY,
            gpt_model=LLM_MODEL_NAME
        )
        return chat_processor.response(messages = messages, temperature = temperature, response_format = response_format)
    
