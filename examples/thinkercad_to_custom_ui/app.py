from circuikit import Circuikit
from circuikit.serial_monitor_interface import (
    ThinkercadInterface,
)
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ThingsBoardGateway, ServiceAdapter, FileLogger
from circuikit.protocols import (
    SendSmiInputFn,
)
from .example_gui import ExampleGUI

from dirty.env import (
    THINKERCAD_URL,
    THINGSBOARD_TOKEN,
    CHROME_PROFILE_PATH,
    READINGS_FILE_LOGGER_PATH,
)


def allocate_services(send_smi_input: SendSmiInputFn) -> list[Service]:
    # initiate gui with fn to send input into smi on demand
    ex_gui = ExampleGUI(send_smi_input_fn=send_smi_input)
    ex_gui_task = ServiceAdapter(
        on_new_message_fn=ex_gui.update_screen, on_start_fn=ex_gui.start
    )

    services: list[Service] = [
        ThingsBoardGateway(token=THINGSBOARD_TOKEN),
        ex_gui_task,
        FileLogger(file_path=READINGS_FILE_LOGGER_PATH),
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
