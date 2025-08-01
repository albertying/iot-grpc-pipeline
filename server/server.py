import grpc
from gen import device_pb2
from gen import device_pb2_grpc

import asyncio

from abc import ABC, abstractmethod

# strategy interface
class DeviceStrategy(ABC):
    @abstractmethod
    def should_send(self, data: any) -> bool:
        pass

class ThermometerStrategy(DeviceStrategy):
    def __init__(self, threshold):
        self.threshold = threshold
    
    def should_send(self, data: any) -> bool:
        if data > self.threshold:
            return True
        else:
            return False
        
class MotionSensorStrategy(DeviceStrategy):
    def __init__(self, state):
        self.state = state
    
    def should_send(self, data: any) -> bool:
        if data == self.state:
            return data
        else:
            return not data

class SmartPlugStrategy(DeviceStrategy):
    def __init__(self, threshold):
        self.threshold = threshold
    
    def should_send(self, data: any) -> bool:
        if data > self.threshold:
            return True
        else:
            return False


class DeviceService(device_pb2_grpc.DeviceServiceServicer):
    async def StreamDeviceData(self, request_iterator, context):

        thermometer_strategy = ThermometerStrategy(100)
        motion_sensor_strategy = MotionSensorStrategy(True)
        smart_plug_strategy = SmartPlugStrategy(450)

        async for data in request_iterator:
            payload_type = data.WhichOneof("payload")
            payload_value = getattr(data, payload_type)

            print(f"received device_id={data.device_id}, type={data.device_type}, timestamp={data.timestamp}, payload_type={payload_type}, payload_value={payload_value}")


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