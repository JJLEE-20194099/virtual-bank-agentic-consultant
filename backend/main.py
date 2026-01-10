from fastapi import FastAPI, WebSocket
import asyncio
from app.service.gateway.grpc_client import STTClient
from app.service.stt import stt_pb2
from app.service.gateway.kafka_producer import publish_transcript

app = FastAPI()
stt_client = STTClient()

@app.websocket("/ws/audio/{session_id}")
async def audio_ws(ws: WebSocket, session_id: str):
    await ws.accept()
    print(f"WS accepted session: {session_id}")

    audio_queue = asyncio.Queue()

    async def audio_gen():
        while True:
            chunk = await audio_queue.get()
            yield stt_pb2.AudioChunk(
                session_id=session_id,
                audio=chunk,
                sample_rate=16000
            )

    async def receive_audio():
        while True:
            data = await ws.receive_bytes()
            await audio_queue.put(data)

    async def send_transcript():
        async for transcript in stt_client.stream(audio_gen()):
            if transcript.text != "":
              publish_transcript(session_id, transcript)
              await ws.send_json({
                  "text": transcript.text,
                  "is_final": transcript.is_final,
                  "language": transcript.language
              })

    await asyncio.gather(
        receive_audio(),
        send_transcript()
    )


from fastapi.responses import HTMLResponse

@app.get("/")
async def get():
    return HTMLResponse("""
        <!DOCTYPE html>
<html>

<body>
  <h1>STT Test</h1>
  <script>
    const ws = new WebSocket("ws://localhost:8000/ws/audio/test123");

    ws.onopen = () => console.log("WS connected");
    ws.onerror = (err) => console.error("WS error", err);
    ws.onclose = (e) => console.log("WS closed", e);

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      console.log("Transcript:", msg.text, msg.is_final);
    };

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      const ctx = new AudioContext({ sampleRate: 16000 });
      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);

      source.connect(processor);
      processor.connect(ctx.destination);

      processor.onaudioprocess = e => {
        const pcm = e.inputBuffer.getChannelData(0);
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(float32ToPCM16(pcm));
        }
      };
    });

    function float32ToPCM16(float32) {
      const buffer = new ArrayBuffer(float32.length * 2);
      const view = new DataView(buffer);
      for (let i = 0; i < float32.length; i++) {
        let s = Math.max(-1, Math.min(1, float32[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      }
      return buffer;
    }
  </script>
</body>

</html>
    """)