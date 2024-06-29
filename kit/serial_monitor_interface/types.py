from dataclasses import dataclass
from .protocols import ConcreteSerialMonitorInterface
from typing import TypedDict


@dataclass(frozen=True, slots=True)
class SerialMonitorOptions:
    interface: ConcreteSerialMonitorInterface
    sample_rate_ms: float

    def __post_init__(self):
        if self.sample_rate_ms < 25:
            raise ValueError("sample_rate_ms must be >= 25")


class Sample(TypedDict):
    time: int
    ...
