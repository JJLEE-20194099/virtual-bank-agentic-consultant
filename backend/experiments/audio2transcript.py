import openai
from dotenv import load_dotenv
import os

class AudioProcessor:
    def __init__(self, api_key: str, gpt_model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.gpt_model = gpt_model
    
    def transcibe_audio(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as audio_file:
                transcript = openai.audio.transcriptions.create(
                    model = "whisper-1",
                    file = audio_file
                )
            return transcript.text
        except Exception as e:
            print("Error in transcribe audio:", e)
            return ""
    

if __name__ == "__main__":

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Can not found OPENAI_API_KEY")
    file_path = "backend/experiments/data/audio/2/speech.mp3"
    processor = AudioProcessor(api_key = api_key)
    transcript = processor.transcibe_audio(file_path = file_path)
    print(transcript)

