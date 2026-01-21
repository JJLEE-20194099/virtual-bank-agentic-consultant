import grpc
import asyncio
import time
from app.service.stt import stt_pb2
from app.service.stt import stt_pb2_grpc
from app.service.stt.asr import transcribe_pcm16

class STTServicer(stt_pb2_grpc.STTServiceServicer):
    def __init__(self):
        pass

    async def StreamAudio(self, request_iterator, context):
        buffer = b"" 
        session_id = None
        last_processed_time = time.time()  
        frame_duration = 20  
        sample_rate = 16000  
        bytes_per_frame = int(sample_rate * 2 * frame_duration / 1000) 
        silence_duration = 0 
        max_silence = 800  

        async for chunk in request_iterator:
            session_id = chunk.session_id
            buffer += chunk.audio  
            current_time = time.time()
            if current_time - last_processed_time >= 5:  
                if buffer:  
                    text, lang = transcribe_pcm16(buffer)
                    if (text.strip() != ""):
                        yield stt_pb2.Transcript(
                            session_id=session_id,
                            text=text,
                            is_final=True, 
                            language=lang
                        )
                    buffer = b""  
                    last_processed_time = current_time  

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
