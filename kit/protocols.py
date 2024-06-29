from typing import Protocol
from circuikit.services import Service


class SendSmiInputFn(Protocol):
    def __call__(self, message: str) -> None: ...


class AllocateServicesFn(Protocol):
    def __call__(self, send_smi_input: SendSmiInputFn) -> list[Service]: ...
