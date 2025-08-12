import grpc
from gen import device_pb2
from gen import device_pb2_grpc

from gen import alert_pb2
from gen import alert_pb2_grpc

import collections

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
            return data == self.state
        else:
            return not data == self.state

class SmartPlugStrategy(DeviceStrategy):
    def __init__(self, threshold):
        self.threshold = threshold
    
    def should_send(self, data: any) -> bool:
        if data > self.threshold:
            return True
        else:
            return False
        


class AlertManager:
    def __init__(self):
        self.subscriptions = collections.defaultdict(set)
        self.clients = {}
    
class AlertService(alert_pb2_grpc.AlertServiceServicer):
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
    async def StreamAlerts(self, request_iterator, context):
        async for request in request_iterator:
            if request.HasField("subscribe"):
                client_id = request.subscribe.client_id
                device_id = request.subscribe.device_id
                self.alert_manager.subscriptions[client_id].add(device_id)
                self.alert_manager.clients[client_id] = context

                yield alert_pb2.AlertResponse(
                    ack = alert_pb2.AckResponse(
                        message = f"Subscribed to {device_id}",
                        success = True
                    )
                )
            elif request.HasField("unsubscribe"):
                client_id = request.unsubscribe.client_id
                device_id = request.unsubscribe.device_id
                self.alert_manager.subscriptions[client_id].discard(device_id)

                yield alert_pb2.AlertResponse(
                    ack = alert_pb2.AckResponse(
                        message = f"Unsubscribed to {device_id}",
                        success = True
                    )
                )
        
            
class DeviceService(device_pb2_grpc.DeviceServiceServicer):
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.device_strategies = {
            device_pb2.THERMOMETER: ThermometerStrategy(100),
            device_pb2.SMART_PLUG: SmartPlugStrategy(450),
            device_pb2.MOTION_SENSOR: MotionSensorStrategy(True)
        }

    async def send_alert_to_subscribers(self, device_id, message, timestamp):
        for client_id, subscribed_devices in self.alert_manager.subscriptions.items():
            if device_id in subscribed_devices:
                context = self.alert_manager.clients.get(client_id)
                if context is not None:
                    alert_response = alert_pb2.AlertResponse(alert = alert_pb2.Alert(device_id = device_id, message = message, timestamp = timestamp))
                    await context.write(alert_response)
        
    async def StreamDeviceData(self, request_iterator, context):

        async for data in request_iterator:
            payload_type = data.WhichOneof("payload")
            payload_value = getattr(data, payload_type)

            print(f"received device_id={data.device_id}, type={data.device_type}, timestamp={data.timestamp}, payload_type={payload_type}, payload_value={payload_value}")

            strategy = self.device_strategies.get(data.device_type)
            if strategy and strategy.should_send(payload_value):
                await self.send_alert_to_subscribers(data.device_id, f"Alert! Value = {payload_value}", data.timestamp)


        return device_pb2.Response(status = "Success")
    
async def serve():
    server = grpc.aio.server()
    alert_manager = AlertManager()
    device_pb2_grpc.add_DeviceServiceServicer_to_server(DeviceService(alert_manager), server)
    alert_pb2_grpc.add_AlertServiceServicer_to_server(AlertService(alert_manager), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("Server started on port 50051")
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())