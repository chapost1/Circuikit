from typing import Protocol


class SendSmiInputFn(Protocol):
    def __call__(self, message: str) -> None: ...
