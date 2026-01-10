from faster_whisper import WhisperModel
import numpy as np
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

print("Loading model...")
model = WhisperModel("small") 
print("Loaded model")


def transcribe_pcm16(pcm_bytes: bytes, sample_rate=16000):
    audio = np.frombuffer(pcm_bytes, np.int16).astype(np.float32) / 32768.0

    segments, info = model.transcribe(audio, beam_size=5, word_timestamps=False, vad_filter=True)
    text = " ".join([seg.text for seg in segments])
    lang = info.language if info.language else "unknown"
    return text, lang
