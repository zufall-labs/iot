# IoT Software Components

## Structure

- **adapters/**: Hardware abstraction layers
  - `adc-adapters/waveshare-ads1263/`: Driver for Waveshare High-Precision AD HAT
  
- **core/**: Core business logic
  - `entropy-generator/`: Chaos-based entropy generation
  - `mqtt-publisher/`: MQTT publishing logic
  
- **tools/**: Development and debugging tools
  - `diagnostics/`: Chaos diagnostic tool

## Setup
```bash
pip install numpy scipy paho-mqtt
```
