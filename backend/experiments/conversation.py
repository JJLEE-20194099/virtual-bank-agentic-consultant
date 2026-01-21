import openai
from dotenv import load_dotenv
import os


class ChatProcessor:
    def __init__(self, api_key: str, gpt_model: str = "gpt-4o"):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.gpt_model = gpt_model

    def chat(self, user_message: str, system_message: str = "You are a helpful assistant.") -> str:
        try:
            completion = openai.chat.completions.create(
                model=self.gpt_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
            )
            return completion.choices[0].message.content
        except Exception as e:
            print("Error in chat completion:", e)
            return ""


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Can not found OPENAI_API_KEY")

    processor = ChatProcessor(
        api_key=api_key,
        gpt_model="gpt-4o"
    )

    response = processor.chat("Tell me about VPBank promotion for customer")
    print(response)
