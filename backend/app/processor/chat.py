import openai
class ChatProcessor:
    def __init__(self, api_key: str, gpt_model: str = "gpt-4o"):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.gpt_model = gpt_model

    def response(self, messages: List, temperature = float, response_format = None) -> str:
        try:
            completion = openai.chat.completions.create(
                model=self.gpt_model,
                messages=messages,
                temperature=temperature,
                response_format=response_format,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print("Error in chat completion:", e)
            return ""