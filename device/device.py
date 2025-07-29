import datetime
import grpc
import device_pb2
import device_pb2_grpc

import asyncio
import random

async def thermometer_device(stream):
    while True:
        asyncio.sleep(3)
        temperature =  60 + (random.randint(0, 300) * .1)
        temperatureData = device_pb2.Data(device_id="thermo_001", timestamp = datetime.utcnow().isoformat() + "Z", device_type=device_pb2.DeviceType.THERMOMETER, temperature = temperature)
        await stream.write(temperatureData)

async def smart_plug_device(stream):
    while True:
        asyncio.sleep(1)
        wattage = (random.randint(0, 15000) * .1)
        wattageData = device_pb2.Data(device_id="smart_out_203", timestamp = datetime.utcnow().isoformat() + "Z", device_type=device_pb2.DeviceType.THERMOMETER, temperature = wattage)
        await stream.write(wattageData)

async def motion_sensor_device(stream):
    while True:
        asyncio.sleep(5)
        motion = random.choice([True, False])
        motionData = device_pb2.Data(device_id="motion_door_507", timestamp = datetime.utcnow().isoformat() + "Z", device_type=device_pb2.DeviceType.THERMOMETER, temperature = motion)
        await stream.write(motionData)
        
async def simulate_devices():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        stream = stub.StreamDeviceData()

        asyncio.gather(
            thermometer_device(stream),
            smart_plug_device(stream),
            motion_sensor_device(stream),
        )

if __name__ == '__main__':
    asyncio.run(simulate_devices())


