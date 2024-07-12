# ⚙️ Circuikit

![Python](https://img.shields.io/badge/python-3.10%2B-purple)
![LTS](https://img.shields.io/badge/LTS-v0.3.6-blue)


## Overview

Circuikit is a Python package designed to facilitate communication between Python applications and Arduino hardware, supporting both simulated environments (like Thinkercad) and real hardware. It enables easy integration with various services for data processing, visualization, and alerts, providing a modular and flexible framework for embedded system projects.

## Table of Contents

<details>
<summary>Click to expand</summary>

- [Overview](#overview)
- [Installation](#installation)
- [Documentation](#documentation)
  - [`Circuikit` Class](#circuikit-class)
  - [`SerialMonitorInterface` Class](#serialmonitorinterface-class)
  - [`SerialMonitorOptions` Class](#serialmonitoroptions-class)
- [Service Integration](#service-integration)
  - [Creating a Custom Service](#creating-a-custom-service)
    - [`ServiceAdapter` Class](#serviceadapter-class)
  - [Using Built-in Services](#using-built-in-services)
    - [`ThingsBoardGateway` Class](#thingsboardgateway-class)
    - [`FileLogger` Class](#filelogger-class)
- [Flexible Serial Monitor Interface](#flexible-serial-monitor-interface)
  - [`ConcreteSerialMonitorInterface` Protocol](#concreteserialmonitorinterface-protocol)
- [ThinkercadInterface](#thinkercadinterface)
  - [Initialization](#initialization)
  - [Key Methods](#key-methods)
  - [Example Usage](#example-usage)
  - [Important Notes](#important-notes)
- [PortInterface](#portinterface)
  - [Initialization](#initialization-1)
  - [Key Methods](#key-methods-1)
  - [Example Usage](#example-usage-1)
  - [Important Notes](#important-notes-1)
- [Contributing](#contributing)
  - [How to run as a sandbox](#how-to-run-as-a-sandbox)
  - [Instructions](#instructions)
  - [Adding New Built-in Services](#adding-new-built-in-services)
  - [Adding New Built-in Serial Monitor Interfaces](#adding-new-built-in-serial-monitor-interfaces)
- [License](#license)
- [Contact](#contact)

</details>

## Installation

To install Circuikit, use pip:

```sh
pip install git+https://github.com/chapost1/Circuikit.git@v0.3.5
```

## Documentation

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

Got it! If users stitch `ServiceAdapter` to their own class functions before passing them to the service list, we can adjust the table of contents and the related sections accordingly. Here's how you can update the table of contents and the relevant sections in your README:

### Service Integration

#### Creating a Custom Service

##### `ServiceAdapter` Class

To create a custom service, define your class and use `ServiceAdapter` to stitch it to your own class functions:

```python
from circuikit.services import ServiceAdapter

class CustomService:
    def on_message(self, message: dict) -> None:
        # Process the message
        print(message)

# Create an instance of your custom service
custom_service = CustomService()

# Use ServiceAdapter to stitch your custom service to a function
service_adapter = ServiceAdapter(on_new_message_fn=custom_service.on_message)
```

#### Using Built-in Services

Circuikit provides built-in services that you can use for various purposes:

##### `ThingsBoardGateway` Class

A service for sending data to ThingsBoard.

**Initialization Parameters:**
- `token`: The ThingsBoard API token.

**Example:**
```python
from circuikit.services import ThingsBoardGateway

thingsboard_service = ThingsBoardGateway(token="YOUR_THINGSBOARD_TOKEN")
```

##### `FileLogger` Class

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

This structure reflects how users can integrate custom and built-in services with Circuikit, using `ServiceAdapter` to stitch their own class functions to the service interface. Adjust the examples and details based on your specific implementation and use cases.

## Flexible Serial Monitor Interface

Circuikit allows using any serial monitor interface by implementing the `ConcreteSerialMonitorInterface` protocol. Thinkercad is just one example. You can create custom interfaces for real hardware or other simulators by following the `ConcreteSerialMonitorInterface` structure.

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
    open_simulation_timeout=10,  # Timeout for simulation to load in seconds
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

Sure, here is the markdown content for the new section on the `PortInterface` class:


### PortInterface

The `PortInterface` is a built-in Serial Monitor Interface (SMI) for Circuikit that enables communication through a PC port using a serial cable. This interface allows you to interact with physical Arduino hardware, making it suitable for projects requiring direct hardware communication.

#### Initialization

To use the `PortInterface`, you need to provide the baud rate and optionally specify other parameters such as the port and whether to detect the port automatically.

```python
from circuikit.serial_monitor_interface import PortInterface

port_interface = PortInterface(
    baudrate=115200,  # Set your baud rate to match your Arduino's
    detect_port_automatically=True,  # Set to True to detect the port automatically
    port=None,  # Optional: Specify the port directly if known
)
```

#### Key Methods

- **start()**: Opens the serial connection with the specified port and baud rate.
- **send_message(message: str)**: Sends a message through the serial port.
- **sample() -> str | None**: Reads data from the serial port and returns it.
- **stop()**: Closes the serial connection.

#### Example Usage

Below is an example of how to integrate the `PortInterface` with Circuikit:

```python
from circuikit import Circuikit
from circuikit.serial_monitor_interface import PortInterface
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import ThingsBoardGateway

serial_monitor_options = SerialMonitorOptions(
    timestamp_field_name="timestamp_ms",  # JSON timestamp field
    interface=PortInterface(
        baudrate=115200,
        port='/dev/cu.usbmodem14101' # In case you know the exact port
    ),
    sample_rate_ms=25,
)

services: list[Service] = [ServiceAdapter(on_new_message_fn=print)]

kit = Circuikit(
    serial_monitor_options=serial_monitor_options,
    services=services,
)

kit.start(block=True)
```

#### Important Notes

- **Port Detection**: If `detect_port_automatically` is set to True, the interface will attempt to detect the Arduino port. If it fails, it will prompt the user to select the correct port.
- **Dependencies**: Make sure your Arduino is fully plugged in using USB Type-B

## Contributing

### How to run as a sandbox
Read the [Examples readme file](./examples/readme.md)

### Instructions

We welcome contributions to Circuikit! If you would like to contribute, please follow these guidelines:

1. **Fork the Repository**: Start by forking the repository to your GitHub account.

2. **Create a Branch**: Create a new branch for your feature or bug fix.

3. **Make Your Changes**: Implement your changes, ensuring that you follow the project's coding standards and guidelines.

4. **Update Documentation**: Update the documentation to reflect your changes, including any new built-in services or features.

5. **Submit a Pull Request**: Once your changes are ready, submit a pull request to the main repository. Provide a detailed description of your changes and the purpose of the contribution.

### Adding New Built-in Services

We are particularly interested in contributions that add new built-in services to Circuikit. If you have a service that you think would be beneficial to other users, please follow the contribution guidelines and submit a pull request.

### Adding New Built-in Serial Monitor Interfaces

You can also contribute by adding new built-in Serial Monitor Interfaces (SMI). If you can provide support for existing interfaces such as Thinkercad to support additional browsers or entirely different simulation environments, your contributions are welcome!

Thank you for your interest in contributing to Circuikit! We appreciate your efforts in helping us improve and expand the capabilities of this project.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

For any questions or suggestions, please feel free to contact us.

> <a href="https://github.com/chapost1"><kbd><img src="https://avatars.githubusercontent.com/u/39523779?s=25"/></kbd></a> &nbsp; Shachar Tal
>
> [Github](https://github.com/chapost1) | [LinkedIn](https://www.linkedin.com/in/shahar-tal-4aa887166/) | [Email](mailto:stalmail10@gmail.com)
