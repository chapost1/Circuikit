from circuikit import Circuikit
from circuikit.serial_monitor_interface import (
    ThinkercadInterface,
)
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ThingsBoardGateway
from circuikit.protocols import (
    SendSmiInputFn,
)

from dirty.env import THINKERCAD_URL, THINGSBOARD_TOKEN, CHROME_PROFILE_PATH


def allocate_services(send_smi_input: SendSmiInputFn) -> list[Service]:
    services: list[Service] = [
        ThingsBoardGateway(token=THINGSBOARD_TOKEN),
    ]

    return services


if __name__ == "__main__":
    serial_monitor_options = SerialMonitorOptions(
        interface=ThinkercadInterface(
            thinkercad_url=THINKERCAD_URL,
            chrome_profile_path=CHROME_PROFILE_PATH,
            open_simulation_timeout=120,
        ),
        sample_rate_ms=25,
    )

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        allocate_services_fn=allocate_services,
    )

    kit.start()
