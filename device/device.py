
import grpc
from gen import device_pb2
from gen import device_pb2_grpc
import asyncio
import random

from datetime import datetime, timezone

async def thermometer_device(stream):
    while True:
        await asyncio.sleep(3)
        temperature =  60 + (random.randint(0, 300) * .1)
        temperatureData = device_pb2.Data(device_id=1, timestamp = datetime.now(timezone.utc).isoformat() + "Z", device_type=device_pb2.DeviceType.THERMOMETER, temperature = device_pb2.TemperatureData(temperature=temperature))
        await stream.write(temperatureData)

async def smart_plug_device(stream):
    while True:
        await asyncio.sleep(1)
        wattage = (random.randint(0, 15000) * .1)
        wattageData = device_pb2.Data(device_id=2, timestamp = datetime.now(timezone.utc).isoformat() + "Z", device_type=device_pb2.DeviceType.SMART_PLUG, wattage = device_pb2.PowerData(wattage=wattage))
        await stream.write(wattageData)

async def motion_sensor_device(stream):
    while True:
        await asyncio.sleep(5)
        motion = random.choice([True, False])
        motionData = device_pb2.Data(device_id=3, timestamp = datetime.now(timezone.utc).isoformat() + "Z", device_type=device_pb2.DeviceType.MOTION_SENSOR, motion = device_pb2.MotionData(motion=motion))
        await stream.write(motionData)
        
async def simulate_devices():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        stream = stub.StreamDeviceData()

        await asyncio.gather(
            thermometer_device(stream),
            smart_plug_device(stream),
            motion_sensor_device(stream),
        )

if __name__ == '__main__':
    asyncio.run(simulate_devices())


