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
        self.queues = {}
    
class AlertService(alert_pb2_grpc.AlertServiceServicer):
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager

    async def StreamAlerts(self, request_iterator, context):
        queue = asyncio.Queue()
        client_id = None

        async def handle_requests():
            nonlocal client_id
            async for request in request_iterator:
                if request.HasField("subscribe"):
                    client_id = request.subscribe.client_id
                    device_id = request.subscribe.device_id
                    self.alert_manager.subscriptions[client_id].add(device_id)
                    self.alert_manager.queues[client_id] = queue

                    await queue.put(alert_pb2.AlertResponse(
                        ack=alert_pb2.AckResponse(
                            message=f"Subscribed to {device_id}",
                            success=True
                        )
                    ))

                elif request.HasField("unsubscribe"):
                    client_id = request.unsubscribe.client_id
                    device_id = request.unsubscribe.device_id
                    self.alert_manager.subscriptions[client_id].discard(device_id)

                    await queue.put(alert_pb2.AlertResponse(
                        ack=alert_pb2.AckResponse(
                            message=f"Unsubscribed from {device_id}",
                            success=True
                        )
                    ))

        request_task = asyncio.create_task(handle_requests())

        while True:
            response = await queue.get()
            yield response

        
            
class DeviceService(device_pb2_grpc.DeviceServiceServicer):
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.device_strategies = {
            device_pb2.THERMOMETER: ThermometerStrategy(65),
            device_pb2.SMART_PLUG: SmartPlugStrategy(200),
            device_pb2.MOTION_SENSOR: MotionSensorStrategy(True)
        }

    async def send_alert_to_subscribers(self, device_id, message, timestamp):
        device_id_str = str(device_id)
        for client_id, subscribed_devices in self.alert_manager.subscriptions.items():
            if device_id_str in subscribed_devices:
                queue = self.alert_manager.queues.get(client_id)
                if queue:
                    await queue.put(alert_pb2.AlertResponse(
                        alert=alert_pb2.AlertNotification(
                            device_id=device_id_str,
                            message=message,
                            timestamp=timestamp
                        )
                    ))
        
    async def StreamDeviceData(self, request_iterator, context):

        async for data in request_iterator:
            payload_type = data.WhichOneof("payload")
            payload_value = getattr(data, payload_type)

            if payload_type == "temperature":
                value = payload_value.temperature
            elif payload_type == "wattage":
                value = payload_value.wattage
            elif payload_type == "motion":
                value = payload_value.motion
            else:
                continue
            print(data.device_id, data.device_type, data.timestamp, value)
            strategy = self.device_strategies.get(data.device_type)
            if strategy and strategy.should_send(value):
                await self.send_alert_to_subscribers(data.device_id, f"Alert! Value = {value}", data.timestamp)
            

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