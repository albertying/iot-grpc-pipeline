import grpc
from gen import device_pb2
from gen import device_pb2_grpc

import asyncio

class DeviceService(device_pb2_grpc.DeviceServiceServicer):
    async def StreamDeviceData(self, request_iterator, context):
        count = 0

        async for data in request_iterator:
            count += 1
            print(f"received: {data.device_type}, {data.device.payload}")

        return device_pb2.Response(status = "Success")
async def serve():
    server = grpc.aio.server()
    device_pb2_grpc.add_DeviceServiceServicer_to_server(DeviceService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("Server started on port 50051")
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())