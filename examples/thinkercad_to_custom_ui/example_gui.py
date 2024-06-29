from .models import Sensors
from circuikit.protocols import SendSmiInputFn


class ExampleGUI:
    def __init__(self, send_smi_input_fn: SendSmiInputFn):
        super().__init__()
        # use this fn to send input into smi
        self.send_smi_input_fn = send_smi_input_fn
        # Do something that init screen window
        # Avoid opening IO descriptors or creating threads in the __init__ method
        # Instead, do it in the start method and supply it as on_start_fn to ServiceAdapter
        ...

    def start(self) -> None:
        print("[ExampleGUI] STARTED")
        # Create it only if needed
        pass

    def update_screen(self, message: dict) -> None:
        # reply_smi_fn will send message to serial monitor interface.
        read = Sensors(**message)
        print(f"[ExampleGUI]: read={read}", flush=True)
        # Does something
        pass
