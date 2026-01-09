import whisper
import numpy as np

model = whisper.load_model("base")

def transcribe_pcm16(pcm_bytes: bytes, sample_rate=16000):
    audio = np.frombuffer(pcm_bytes, np.int16).astype(np.float32) / 32768.0
    result = model.transcribe(audio, language=None, fp16=False)
    return result["text"], result["language"]
