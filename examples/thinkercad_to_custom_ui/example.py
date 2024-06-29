from circuikit import Circuikit
from circuikit.serial_monitor_interface import (
    ThinkercadInterface,
)
from circuikit.serial_monitor_interface.types import SerialMonitorOptions
from circuikit.services import Service, ThingsBoardGateway, ServiceAdapter, FileLogger
from .example_gui import ExampleGUI


def run_example() -> None:
    serial_monitor_options = SerialMonitorOptions(
        interface=ThinkercadInterface(
            thinkercad_url="https://google.com",  # Change it to something else
            open_simulation_timeout=120,
        ),
        sample_rate_ms=25,
    )

    ex_gui = ExampleGUI()
    ex_gui_task = ServiceAdapter(on_new_message_fn=ex_gui.update_screen)

    services: list[Service] = [
        ThingsBoardGateway(token=""),
        ex_gui_task,
        FileLogger(file_path="./dirty/logs/sensors.txt"),
    ]

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        services=services,
    )

    # set fn to send input into serial monitor as input on demand
    # for example if user press on gui button
    ex_gui.set_send_smi_input_fn(send_smi_input_fn=kit.send_smi_input)
    # kit is not blocking by default, but it is a good practice to be explicit
    kit.start(block=False)

    # usually gui apps need to run on the main thread and is a blocking operation
    # so it's a good practice to start it last thing on the program
    ex_gui.start()
