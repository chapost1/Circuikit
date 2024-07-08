# Circuikit

![Python](https://img.shields.io/badge/python-3.10%2B-purple)
![LTS](https://img.shields.io/badge/LTS-v0.3.5-blue)


## Overview

Circuikit is a Python package designed to facilitate communication between Python applications and Arduino hardware, supporting both simulated environments (like Thinkercad) and real hardware. It enables easy integration with various services for data processing, visualization, and alerts, providing a modular and flexible framework for embedded system projects.

## Installation

To install Circuikit, use pip:

```sh
pip install git+https://github.com/chapost1/Circuikit.git@v0.3.5
```

## Quick Start

### Basic Example

Here is a basic example of how to connect a Thinkercad project to ThingsBoard:

```python
from circuikit import Circuikit
from circuikit.serial_monitor_interface import ThinkercadInterface
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ThingsBoardGateway

def run_example() -> None:
    serial_monitor_options = SerialMonitorOptions(
        timestamp_field_name="timestamp_ms",  # Default is 'time'
        interface=ThinkercadInterface(
            thinkercad_url="https://google.com",  # Change to your Thinkercad URL
            open_simulation_timeout=120,
        ),
        sample_rate_ms=25,
    )

    services: list[Service] = [
        ThingsBoardGateway(token="YOUR_THINGSBOARD_TOKEN"),
    ]

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        services=services,
    )
    kit.start(block=True)

if __name__ == "__main__":
    run_example()
```

### Radar Example

This example demonstrates creating a radar system using multiple ultrasonic sensors and a servo motor. Note that this is just an example, and you can build various projects using Circuikit.

```python
from circuikit import Circuikit
from circuikit.serial_monitor_interface import ThinkercadInterface
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ServiceAdapter
import services.notifier as notifier
import services.radar as radar
from utils import osx
from functools import partial
from models import Sensors
import logging

logging.basicConfig(level=logging.INFO)

from dirty.env import (
    THINKERCAD_URL,
    THINKERCAD_OPEN_SIMULATION_TIMEOUT,
    SERIAL_MONITOR_SAMPLE_RATE_MS,
    SMS_DESTINATION_PHONE_NUMBER,
)

if __name__ == "__main__":
    serial_monitor_options = SerialMonitorOptions(
        timestamp_field_name=Sensors.get_time_field_name(),
        interface=ThinkercadInterface(
            thinkercad_url=THINKERCAD_URL,
            open_simulation_timeout=THINKERCAD_OPEN_SIMULATION_TIMEOUT,
        ),
        sample_rate_ms=SERIAL_MONITOR_SAMPLE_RATE_MS,
    )

    radar_gui = radar.RadarGUI()

    alert_manager = notifier.AlertManager(
        notification_channels=[
            notifier.NotificationChannel(
                notify_fn=partial(
                    osx.send_sms, phone_number=SMS_DESTINATION_PHONE_NUMBER
                )
            )
        ]
    )

    radar_service = radar.Radar(
        emit_state_fns=[radar_gui.on_new_data],
        detect_objects_fn=radar.detect_objects,
        alert_fn=alert_manager.on_new_alert,
    )

    services: list[Service] = [
        ServiceAdapter(on_new_message_fn=radar_service.on_new_sensors),
    ]

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        services=services,
    )
    kit.start(block=False)
    radar_gui.start_mainloop()
```

## Detailed Documentation

### `Circuikit` Class

The `Circuikit` class is the core of the package, managing the communication between the Arduino serial monitor and the Python application, and coordinating the services.

**Initialization Parameters:**
- `serial_monitor_options`: An instance of `SerialMonitorOptions` to configure the serial monitor interface.
- `services`: A list of `Service` instances that process the data read from the serial monitor.

**Methods:**
- `start(block=False)`: Starts the Circuikit system. If `block` is `True`, the function will block the main thread.
- `stop()`: Stops the Circuikit system.
- `send_smi_input(message: str)`: Sends a message to the serial monitor interface.

### `SerialMonitorInterface` Class

The `SerialMonitorInterface` class handles the communication with the Arduino serial monitor, reading data, and sending messages.

**Initialization Parameters:**
- `options`: An instance of `SerialMonitorOptions`.
- `on_next_read`: A callable that processes new data reads.
- `messages_to_send_queue`: A queue for messages to be sent to the serial monitor.

**Methods:**
- `start()`: Starts the serial monitor interface.
- `stop()`: Stops the serial monitor interface.
- `send_message(message: str)`: Sends a message to the serial monitor.

### `SerialMonitorOptions` Class

The `SerialMonitorOptions` class is used to configure the serial monitor interface.

**Attributes:**
- `interface`: An instance of a class implementing the `ConcreteSerialMonitorInterface`.
- `sample_rate_ms`: The sampling rate in milliseconds (must be >= 25 ms).
- `timestamp_field_name`: The name of the timestamp field in the JSON data (default is "time").

### Service Integration

Circuikit supports integrating various services to process the data read from the Arduino. 

#### Creating a Custom Service

To create a custom service, subclass the `Service` class and implement the `on_message` method.

```python
from circuikit.services import Service

class CustomService(Service):
    def on_message(self, message: dict) -> None:
        # Process the message
        print(message)
```

#### Using Built-in Services

Circuikit comes with several built-in services, such as `ThingsBoardGateway` and `FileLogger`.

**ThingsBoardGateway**

A service for sending data to ThingsBoard.

**Initialization Parameters:**
- `token`: The ThingsBoard API token.

**Example:**
```python
from circuikit.services import ThingsBoardGateway

thingsboard_service = ThingsBoardGateway(token="YOUR_THINGSBOARD_TOKEN")
```

**FileLogger**

A service for logging data to a file.

**Initialization Parameters:**
- `file_path`: The path to the log file.
- `flush_treshold`: The number of messages before the log is flushed (default is 100).
- `mode`: The file mode (default is "w+").

**Example:**
```python
from circuikit.services import FileLogger

file_logger_service = FileLogger(file_path="logs/data.log")
```

## Flexible Serial Monitor Interface

Circuikit allows using any serial monitor interface by implementing the `ConcreteSerialMonitorInterface` protocol. Thinkercad is just one example. You can create custom interfaces for real hardware or other simulators by following the `ConcreteSerialMonitorInterface` structure.

### Serial Monitor Interface Protocol

The `SerialMonitorInterface` in Circuikit is designed to handle communication between Circuikit and various serial monitor interfaces, such as Thinkercad or physical hardware. To achieve this, the interface relies on a protocol that defines the essential methods any serial monitor interface must implement. This allows for easy adaptation to different environments and ensures consistent communication.

#### ConcreteSerialMonitorInterface Protocol

The `ConcreteSerialMonitorInterface` is a protocol that outlines the required methods any concrete implementation must have. These methods handle starting, stopping, sending messages to, and sampling data from the serial monitor.

```python
from typing import Protocol

class ConcreteSerialMonitorInterface(Protocol):
    def send_message(self, message: str) -> None:
        """Send a message to the serial monitor."""
        pass

    def sample(self) -> str | None:
        """Sample data from the serial monitor."""
        pass

    def start(self) -> None:
        """Start the serial monitor interface."""
        pass

    def stop(self) -> None:
        """Stop the serial monitor interface."""
        pass
```

#### Explanation of Methods

- **send_message(self, message: str) -> None**: 
  - This method sends a message to the serial monitor. It takes a single argument, `message`, which is the string to be sent.

- **sample(self) -> str | None**: 
  - This method samples data from the serial monitor. It returns a string containing the sampled data, or `None` if no data is available.

- **start(self) -> None**: 
  - This method starts the serial monitor interface. It is responsible for initializing any necessary resources or connections.

- **stop(self) -> None**: 
  - This method stops the serial monitor interface. It handles cleanup and resource deallocation.

### ThinkercadInterface

The `ThinkercadInterface` is a built-in Serial Monitor Interface (SMI) for Circuikit that enables communication with a Thinkercad simulation through a Chrome browser. This interface allows you to interact with the Thinkercad environment programmatically, making it suitable for scenarios where physical hardware is not available.

#### Initialization

To use the `ThinkercadInterface`, you need to provide the Thinkercad URL and optionally specify other parameters such as the Chrome profile path and the debugger port.

```python
from circuikit.serial_monitor_interface import ThinkercadInterface

thinkercad_interface = ThinkercadInterface(
    thinkercad_url="https://your-thinkercad-project-url",
    chrome_profile_path=None,  # Optional: Path to Chrome user profile
    debugger_port=8989,  # Optional: Port for Chrome debugging
    open_simulation_timeout=10,  # Timeout for simulation to load
)
```

#### Key Methods

- **start()**: Initializes the Chrome WebDriver, opens the Thinkercad simulation, and sets up the serial monitor.
- **send_message(message: str)**: Sends a message to the Thinkercad serial monitor.
- **sample() -> str | None**: Samples the Thinkercad serial monitor output and returns the latest data.
- **stop()**: Stops the WebDriver and closes the Chrome browser.

#### Example Usage

Below is an example of how to integrate the `ThinkercadInterface` with Circuikit:

```python
from circuikit import Circuikit
from circuikit.serial_monitor_interface import ThinkercadInterface
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import ThingsBoardGateway

serial_monitor_options = SerialMonitorOptions(
    timestamp_field_name="timestamp_ms",  # JSON timestamp field
    interface=ThinkercadInterface(
        thinkercad_url="https://your-thinkercad-project-url",
        open_simulation_timeout=120,
    ),
    sample_rate_ms=25,
)

services = [
    ThingsBoardGateway(token="your-thingsboard-token"),
]

kit = Circuikit(
    serial_monitor_options=serial_monitor_options,
    services=services,
)

kit.start(block=True)
```

#### Important Notes

- **Browser Support**: Currently, `ThinkercadInterface` only supports the Chrome browser. Contributions to support additional browsers are welcome.
- **Dependencies**: This interface relies on the Selenium WebDriver for browser automation. Ensure you have the necessary Selenium and ChromeDriver dependencies installed.

By using the `ThinkercadInterface`, you can simulate your projects in Thinkercad and seamlessly integrate them with Circuikit for advanced data handling and service integration.

## Contributing

We welcome contributions to Circuikit! If you would like to contribute, please follow these guidelines:

1. **Fork the Repository**: Start by forking the repository to your GitHub account.

2. **Create a Branch**: Create a new branch for your feature or bug fix.

3. **Make Your Changes**: Implement your changes, ensuring that you follow the project's coding standards and guidelines.

4. **Update Documentation**: Update the documentation to reflect your changes, including any new built-in services or features.

5. **Submit a Pull Request**: Once your changes are ready, submit a pull request to the main repository. Provide a detailed description of your changes and the purpose of the contribution.

### Adding New Built-in Services

We are particularly interested in contributions that add new built-in services to Circuikit. If you have a service that you think would be beneficial to other users, please follow the contribution guidelines and submit a pull request.

### Adding New Built-in Serial Monitor Interfaces

You can also contribute by adding new built-in Serial Monitor Interfaces (SMI). Currently, Circuikit utilizes a Thinkercad interface that uses Chrome for interaction. If you can provide support for additional browsers or different simulation environments, your contributions are welcome!

Thank you for your interest in contributing to Circuikit! We appreciate your efforts in helping us improve and expand the capabilities of this project.

### To run as a sandbox
Read the [Examples readme file](./examples/readme.md)

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

For any questions or suggestions, please feel free to contact us at [stalmail10@gmail.com](mailto:stalmail10@gmail.com).
