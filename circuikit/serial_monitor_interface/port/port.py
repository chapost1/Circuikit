import serial
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo
import logging

logger = logging.getLogger(__name__)


def find_arduino_port() -> str:
    ports = serial.tools.list_ports.comports()

    arduino_ports = list(filter(lambda p: "Arduino" in p.description, ports))
    if not arduino_ports:
        print("Could not find an arduino - is it plugged in?")
        port = select_port(ports)
        return port.device
    if len(arduino_ports) > 1:
        print("Multiple Arduinos found - using the first")
        return arduino_ports[0].device
    else:
        return arduino_ports[0].device


def select_port(arduino_ports: list[ListPortInfo]) -> ListPortInfo:
    choices = list(map(lambda p: p.name, arduino_ports))
    print("Detected Ports:")
    for i, item in enumerate(choices, 1):
        print(f"{i}. {item}")

    try:
        choice = int(
            input(
                "Enter the number of the correct port (anything else will stop the process): "
            )
        )
        if 1 <= choice <= len(choices):
            selected_port = arduino_ports[choice - 1]
        else:
            raise ValueError("No supported arduino port selected")
    except ValueError:
        raise ValueError("No supported arduino port selected")

    return selected_port


class PortInterface:
    __slots__ = ("serial",)

    def __init__(
        self,
        baudrate: int,
        detect_port_automatically: bool = True,
        port: str | None = None,
    ):
        if port is None:
            if detect_port_automatically:
                port = find_arduino_port()
            else:
                raise ValueError(
                    "Either serial port must be specified or detect_port_automatically should be True"
                )
        else:
            # continue with port
            ...

        # timeout=0 means block=False
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=0)

    def __destroy__(self):
        self.stop()

    def send_message(self, message: str) -> None:
        self.serial.write(message.encode(encoding="utf-8"))

    def sample(self) -> str | None:
        return "\n".join(
            map(
                lambda s_bytes: s_bytes.decode(encoding="utf-8")
                .strip("\r\n")
                .strip("\n"),
                self.serial.readlines(),
            )
        )

    def start(self) -> None:
        self.serial.open()

    def stop(self) -> None:
        self.serial.close()
