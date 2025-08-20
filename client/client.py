import grpc
from gen import alert_pb2
from gen import alert_pb2_grpc
import asyncio


async def send_requests(stream):
    loop = asyncio.get_running_loop()
    print("Enter commands:")
    print("subscribe client1 device123")
    print("unsubscribe client1 device123")

    while True:
        user_input = await loop.run_in_executor(None, input, "> ")

        parts = user_input.strip().split()
        if len(parts) < 3:
            print("Incorrect arg count")
            continue
        command, client_id, device_id = parts

        if command == "subscribe":
            request = alert_pb2.AlertRequest(
                subscribe=alert_pb2.SubscribeRequest(
                    client_id=client_id, device_id=device_id
                )
            )
        elif command == "unsubscribe":
            request = alert_pb2.AlertRequest(
                unsubscribe=alert_pb2.UnsubscribeRequest(
                    client_id=client_id, device_id=device_id
                )
            )
        else:
            print("Unknown command")
            continue
        await stream.write(request)


async def receive_responses(stream):
    async for response in stream:
        if response.HasField("ack"):
            print(f"[ACK] {response.ack.message} | Success: {response.ack.success}")
        elif response.HasField("alert"):
            print(
                f"[ALERT] {response.alert.device_id}: {response.alert.message} at {response.alert.timestamp}"
            )


async def run():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = alert_pb2_grpc.AlertServiceStub(channel)

        stream = stub.StreamAlerts()

        send_task = asyncio.create_task(send_requests(stream))
        receive_task = asyncio.create_task(receive_responses(stream))

        await asyncio.gather(send_task, receive_task)


if __name__ == "__main__":
    asyncio.run(run())
