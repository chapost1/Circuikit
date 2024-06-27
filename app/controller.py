from .models import Sensors
from typing import Callable
import threading
import time


class Controller:
    __slots__ = (
        "write_message_fn",
        "stop_event",
    )

    def __init__(self, write_message_fn: Callable[[str], None]):
        self.write_message_fn = write_message_fn
        self.stop_event = threading.Event()

    def __destroy__(self):
        self.stop_event.set()

    def on_new_read(self, new_read: Sensors):
        print(f"[CONTROLLER]: {new_read}", flush=True)

    def _weird_logic(self) -> None:
        while not self.stop_event.is_set():
            message = "<some_num=4 some_num2=14 some_str=hakuna matata>"
            self.write_message_fn(message)
            time.sleep(5)

    def start_randomally_send_message(self):
        # Delete this wierd logic and implement your own

        t = threading.Thread(
            target=self._weird_logic, args=(self.stop_event,), daemon=True
        )
        t.start()
