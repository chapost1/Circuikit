from circuikit import Circuikit
from circuikit.serial_monitor_interface import (
    PortInterface,
)
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ServiceAdapter


def run_example() -> None:
    serial_monitor_options = SerialMonitorOptions(
        timestamp_field_name="timestamp_ms",  # you can select your own expected JSON timestamp field. default is 'time'
        interface=PortInterface(baudrate=115200),
        sample_rate_ms=25,
    )

    services: list[Service] = [ServiceAdapter(on_new_message_fn=print)]

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        services=services,
    )
    # If there is nothing that keep the process from exit so pass block=True to the start command
    kit.start(block=True)
