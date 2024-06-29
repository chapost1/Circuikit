from circuikit import Circuikit
from circuikit.serial_monitor_interface import (
    ThinkercadInterface,
)
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ThingsBoardGateway
from circuikit.protocols import (
    SendSmiInputFn,
)


def allocate_services(send_smi_input: SendSmiInputFn) -> list[Service]:
    services: list[Service] = [
        ThingsBoardGateway(token=""),
    ]

    return services


def run_example() -> None:
    serial_monitor_options = SerialMonitorOptions(
        interface=ThinkercadInterface(
            thinkercad_url="YOUR_URL",
            open_simulation_timeout=120,
        ),
        sample_rate_ms=25,
    )

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        allocate_services_fn=allocate_services,
    )

    kit.start()
