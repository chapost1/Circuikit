from kit import Kit
from kit.serial_monitor_interface import (
    ThinkercadInterface,
)
from kit.services import Service, ServiceAdapter, ThingsBoardGateway, FileLogger
from example_gui import ExampleGUI

from dirty.env import (
    THINKERCAD_URL,
    SELENIUM_DEBUGGER_PORT,
    SERIAL_MONITOR_SAMPLE_RATE_MS,
    THINGSBOARD_TOKEN,
    READINGS_FILE_LOGGER_PATH,
)

if __name__ == "__main__":
    serial_monitor_interface = ThinkercadInterface(
        thinkercad_url=THINKERCAD_URL, debugger_port=SELENIUM_DEBUGGER_PORT
    )

    ex_gui = ExampleGUI()
    ex_gui_task = ServiceAdapter(
        on_new_message_fn=ex_gui.update_screen,
        on_start_fn=ex_gui.start
    )

    tasks: list[Service] = [
        ThingsBoardGateway(token=THINGSBOARD_TOKEN),
        ex_gui_task,
        FileLogger(file_path=READINGS_FILE_LOGGER_PATH),
    ]

    kit = Kit(
        serial_monitor_interface=serial_monitor_interface,
        sample_rate_ms=SERIAL_MONITOR_SAMPLE_RATE_MS,
        sub_services=tasks,
    )

    kit.start()
