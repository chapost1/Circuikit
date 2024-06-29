from .models import Sensors
from circuikit.protocols import SendSmiInputFn


class ExampleGUI:
    def __init__(self):
        # use this fn to send input into smi
        self.send_smi_input_fn = None
        # Do something that init screen window
        ...

    def set_send_smi_input_fn(self, send_smi_input_fn: SendSmiInputFn) -> None:
        self.send_smi_input_fn = send_smi_input_fn

    def start(self) -> None:
        print("[ExampleGUI] STARTED")
        # usually some blocking stuff

    def update_screen(self, message: dict) -> None:
        # reply_smi_fn will send message to serial monitor interface.
        read = Sensors(**message)
        print(f"[ExampleGUI]: read={read}", flush=True)
        # Does something, maybe calling self.send_smi_input_fn
