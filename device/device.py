import datetime
import grpc
import device_pb2
import device_pb2_grpc

import asyncio
import random

async def thermometer():
    # return a number from 60 to 90 with .1 increments e.g. 70.2, 60.9
    asyncio.sleep(3)
    return 60 + (random.randint(0, 300) * .1)

async def smart_plug():
    asyncio.sleep(1)
    return (random.randint(0, 15000) * .1)

async def motion_sensor():
    asyncio.sleep(5)
    return random.choice([True, False])

async def simulate_devices():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = device_pb2_grpc.DeviceServiceStub(channel)

        stream = stub.StreamDeviceData()

        while True:
            temperature = await thermometer()
            wattage = await smart_plug()
            motion = await motion_sensor()

            temperatureData = device_pb2.Data(device_id="thermo_001", timestamp = datetime.utcnow().isoformat() + "Z", device_type=thermometer, temperature = temperature)
            wattageData = device_pb2.Data(device_id="smart_out_203", timestamp = datetime.utcnow().isoformat() + "Z", device_type=smart_plug, temperature = wattage)
            motionData = device_pb2.Data(device_id="motion_door_507", timestamp = datetime.utcnow().isoformat() + "Z", device_type=motion_sensor, temperature = motion)

            await stream.write(temperatureData)
            await stream.write(wattageData)
            await stream.write(motionData)

if __name__ == '__main__':
    asyncio.run(simulate_devices())


