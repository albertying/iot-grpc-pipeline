import grpc
from gen import alert_pb2
from gen import alert_pb2_grpc
import asyncio

async def run():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = alert_pb2_grpc.AlertServiceStub(channel)

        stream = stub.StreamAlerts()
        

if __name__ == '__main__':
    asyncio.run(run())
