from typing import Protocol


class ReplySmiFn(Protocol):
    def __call__(self, message: str) -> None:
        pass
