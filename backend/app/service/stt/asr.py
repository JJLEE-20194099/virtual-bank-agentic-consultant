import whisper
import numpy as np

print("Loading model...")
model = whisper.load_model("base")
print("Loaded model")

def transcribe_pcm16(pcm_bytes: bytes, sample_rate=16000):
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    result = model.transcribe(audio, language="en", task="transcribe", fp16=False)

    text = result['text']
    lang = result.get('language', "unknown")
    return text, lang
