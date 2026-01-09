from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()

@app.websocket("/ws/audio/{session_id}")
async def audio_stream(ws: WebSocket, session_id: str):
    await ws.accept()
    try:
        while True:
            audio_chunk = await ws.receive_bytes()
            await send_to_stt(session_id, audio_chunk)
    except Exception as e:
        print("Connection closed", e)