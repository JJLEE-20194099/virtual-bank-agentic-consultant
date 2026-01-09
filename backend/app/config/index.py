from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL_NAME =  "gpt-4o"
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
