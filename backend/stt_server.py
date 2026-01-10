import grpc
import asyncio
from app.service.stt import stt_pb2
from app.service.stt import stt_pb2_grpc
from app.service.stt.asr import transcribe_pcm16

class STTServicer(stt_pb2_grpc.STTServiceServicer):

    async def StreamAudio(self, request_iterator, context):
        buffer = b""
        session_id = None

        async for chunk in request_iterator:
            session_id = chunk.session_id
            buffer += chunk.audio

            if len(buffer) >= 32000:
                text, lang = transcribe_pcm16(buffer)

                yield stt_pb2.Transcript(
                    session_id=session_id,
                    text=text,
                    is_final=False,
                    language=lang
                )

                buffer = b""

        if buffer:
            text, lang = transcribe_pcm16(buffer)
            yield stt_pb2.Transcript(
                session_id=session_id,
                text=text,
                is_final=True,
                language=lang
            )

async def serve():
    server = grpc.aio.server()
    stt_pb2_grpc.add_STTServiceServicer_to_server(STTServicer(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("✅ gRPC server running on port 50051")
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
