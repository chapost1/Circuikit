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


def allocate_services(send_smi_input: SendSmiInputFn) -> list[Service]:
    # initiate gui with fn to send input into smi on demand
    ex_gui = ExampleGUI(send_smi_input_fn=send_smi_input)
    ex_gui_task = ServiceAdapter(
        on_new_message_fn=ex_gui.update_screen, on_start_fn=ex_gui.start
    )

    services: list[Service] = [
        ThingsBoardGateway(token=""),
        ex_gui_task,
        FileLogger(file_path="./dirty/logs/sensors.txt"),
    ]

    return services


def run_example() -> None:
    serial_monitor_options = SerialMonitorOptions(
        interface=ThinkercadInterface(
            thinkercad_url="SOME_URL",
            open_simulation_timeout=120,
        ),
        sample_rate_ms=25,
    )

    kit = Circuikit(
        serial_monitor_options=serial_monitor_options,
        allocate_services_fn=allocate_services,
    )

    kit.start()
