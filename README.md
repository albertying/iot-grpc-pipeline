# IoT Alerts System

A gRPC-based IoT Alert System in Python. Devices (thermometers, smart plugs, motion sensors) stream data to a central server. Clients can subscribe/unsubscribe to specific devices and receive alerts when thresholds are exceeded.

## Architecture Overview

1. **DeviceService**: Receives streaming data from IoT devices.
2. **AlertService**: Handles client subscriptions and sends alerts back.
3. **Strategies**: Define alerting conditions per device type:
   - **Thermometer**: temperature > 65°C
   - **Smart Plug**: wattage > 200W
   - **Motion Sensor**: motion detected = True
4. Implemented using Python `grpc.aio` and `asyncio`.

## How It Works

1. Devices send continuous data to the server.
2. Server applies strategy rules.
3. Subscribed clients receive:
   - **ACKs** for subscribe/unsubscribe requests
   - **Alerts** when threshold conditions are met

## Device IDs

| Device ID | Device Type   |
| --------- | ------------- |
| 1         | Thermometer   |
| 2         | Smart Plug    |
| 3         | Motion Sensor |

## Requirements

1. Python 3.9+
2. Dependencies:
   ```bash
   pip install grpcio grpcio-tools protobuf
   ```

## Setup / Installation

1. Start the server:
   ```bash
   python -m server.server
   ```
2. Run the device simulator:
   ```bash
   python -m device.device
   ```
3. Start the client:
   ```bash
   python -m client.client
   ```

## Client Commands

1. Subscribe to a device:
   ```bash
   subscribe <client_id> <device_id>
   ```
2. Unsubscribe from a device:
   ```bash
   unsubscribe <client_id> <device_id>
   ```

## Examples

```bash
subscribe client1 1  # Subscribe to thermometer
subscribe client1 3  # Subscribe to motion sensor
unsubscribe client1 2  # Unsubscribe from smart plug
```

## Example output

```bash
> subscribe client 1
> [ACK] Subscribed to 1 | Success: True
[ALERT] 1: Alert! Value = 81.4000015258789 at 2025-08-20T16:04:18.438811+00:00Z
[ALERT] 1: Alert! Value = 73.0999984741211 at 2025-08-20T16:04:21.445902+00:00Z
```

## Future Improvements

1. Add a web dashboard using WebSockets
2. Implement more robust error handling
