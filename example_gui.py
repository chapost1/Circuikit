from models import Sensors
from kit.services.types import ReplySmiFn


class ExampleGUI:
    def __init__(self):
        super().__init__()
        # Do something that init screen window
        # Avoid opening IO descriptors or creating threads in the __init__ method
        # Instead, do it in the start method and supply it as on_start_fn to ServiceAdapter
        ...

    def start(self) -> None:
        print("ExampleGUI STARTED")
        # Create it only if needed
        pass

    def update_screen(self, message: dict, reply_smi_fn: ReplySmiFn) -> None:
        # reply_smi_fn will send message to serial monitor interface.
        read = Sensors(**message)
        print(f"[ExampleGUI]: read={read}", flush=True)
        # Does something
        pass
