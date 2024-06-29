from .service import Service
from typing import Callable


class ServiceAdapter(Service):
    """Acts as a wrapper that transmit non-service superset the sensors as it was one"""

    def __init__(
        self,
        on_new_message_fn: Callable[[dict], None],
    ):
        super().__init__()
        self.on_new_message_fn = on_new_message_fn

    def on_message(self, message: dict) -> None:
        self.on_new_message_fn(message)
