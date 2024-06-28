from .service import Service
from typing import Callable
from .types import ReplySmiFn


class ServiceAdapter(Service):
    """Acts as a wrapper that transmit non-task superset the sensors as it was one"""

    def __init__(
        self,
        on_new_message_fn: Callable[[dict, ReplySmiFn], None],
        on_start_fn: Callable[[], None] | None = None,
    ):
        super().__init__()
        self.on_new_message_fn = on_new_message_fn
        self.on_start_fn = on_start_fn

    def on_message(self, message: dict, reply_smi_fn: ReplySmiFn) -> None:
        self.on_new_message_fn(message, reply_smi_fn)

    def start(self) -> None:
        super().start()
        if self.on_start_fn is not None:
            self.on_start_fn()
