from kit import Kit
from kit.serial_monitor_interface import (
    ThinkercadInterface,
)
from kit.services import Service, ServiceAdapter, ThingsBoardGateway, FileLogger
from kit.protocols import (
    SendSmiInputFn,
)
from example_gui import ExampleGUI

from dirty.env import (
    THINKERCAD_URL,
    THINKERCAD_CHROME_PROFILE_PATH,
    THINKERCAD_OPEN_SIMULATION_TIMEOUT,
    SERIAL_MONITOR_SAMPLE_RATE_MS,
    THINGSBOARD_TOKEN,
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
    serial_monitor_interface = ThinkercadInterface(
        thinkercad_url=THINKERCAD_URL,
        chrome_profile_path=THINKERCAD_CHROME_PROFILE_PATH,
        open_simulation_timeout=THINKERCAD_OPEN_SIMULATION_TIMEOUT,
    )

    kit = Kit(
        serial_monitor_interface=serial_monitor_interface,
        sample_rate_ms=SERIAL_MONITOR_SAMPLE_RATE_MS,
        allocate_services_fn=allocate_services,
    )

    kit.start()
