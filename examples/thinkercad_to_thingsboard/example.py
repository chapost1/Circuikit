from circuikit import Circuikit
from circuikit.serial_monitor_interface import (
    ThinkercadInterface,
)
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ThingsBoardGateway


def run_example() -> None:
    serial_monitor_options = SerialMonitorOptions(
        interface=ThinkercadInterface(
            thinkercad_url="https://google.com",  # Change it to something else
            open_simulation_timeout=120,
        ),
        sample_rate_ms=25,
    )

    services: list[Service] = [
        ThingsBoardGateway(token=""),
    ]

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        services=services,
    )
    # If there is nothing that keep the process from exit so pass block=True to the start command
    kit.start(block=True)
