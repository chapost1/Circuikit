import serial
import serial.tools.list_ports
from serial.tools.list_ports_common import ListPortInfo
import logging

logger = logging.getLogger(__name__)


def select_port(arduino_ports: list[ListPortInfo]) -> ListPortInfo:
    choices = list(map(lambda p: f'{p.device} - {p.description}', arduino_ports))
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


def find_arduino_port() -> ListPortInfo:
    ports = serial.tools.list_ports.comports()

    arduino_ports = list(filter(lambda p: "Arduino" in p.description, ports))
    if not arduino_ports:
        print("Could not find an arduino - is it plugged in?")
        port = select_port(ports)
        return port
    if len(arduino_ports) > 1:
        print("Multiple Arduinos found - using the first")
        return arduino_ports[0]
    else:
        return arduino_ports[0]


def compute_port(fixed_port: str | None, detect_port_automatically: bool) -> str:
    if fixed_port is not None:
        # continue with oritinal port
        return fixed_port

    if detect_port_automatically:
        found_port = find_arduino_port()
        return found_port.device
    else:
        raise ValueError(
            "Either serial port must be specified or detect_port_automatically should be True"
        )


class PortInterface:
    __slots__ = ("serial", "port", "baudrate")

    def __init__(
        self,
        baudrate: int,
        detect_port_automatically: bool = True,
        port: str | None = None,
    ):
        self.serial = None
        self.baudrate = baudrate
        # findint arduino port might involve taking input from user in case of auto detection failure.
        # taking user input when multiprocessing is involved can be complex, to avoid those kind of complexities
        # it happens on __init__
        self.port = compute_port(
            fixed_port=port, detect_port_automatically=detect_port_automatically
        )

    def __destroy__(self):
        self.stop()

    def send_message(self, message: str) -> None:
        if self._is_serial_open():
            self.serial.write(message.encode(encoding="utf-8"))
        else:
            ...

    def sample(self) -> str | None:
        if self._is_serial_open():
            return "\n".join(
                map(
                    lambda s_bytes: s_bytes.decode(encoding="utf-8")
                    .strip("\r\n")
                    .strip("\n"),
                    self.serial.readlines(),
                )
            )
        else:
            return None

    def start(self) -> None:
        if self._is_serial_open():
            ...
        # timeout=0 means block=False
        self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=0)
        # try:
        if not self.serial.is_open:
            self.serial.open()

    def stop(self) -> None:
        if self._is_serial_open():
            self.serial.close()

    def _is_serial_open(self) -> bool:
        return self.serial is not None and self.serial.is_open
