import grpc
from app.service.stt import stt_pb2, stt_pb2_grpc


class STTClient:
    def __init__(self, target="localhost:50051"):
        self.channel = grpc.aio.insecure_channel(target)
        self.stub = stt_pb2_grpc.STTServiceStub(self.channel)

    async def stream(self, audio_generator):
        async for transcript in self.stub.StreamAudio(audio_generator):
            yield transcript
