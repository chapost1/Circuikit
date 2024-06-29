from typing import Protocol


class ConcreteSerialMonitorInterface(Protocol):
    def send_message(self, message: str) -> None:
        pass

    def sample(self) -> str | None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class QueueProtocol(Protocol):
    def get(self):
        pass

    def put(self, obj, block: bool = True, timeout: float | None = None) -> None:
        pass
