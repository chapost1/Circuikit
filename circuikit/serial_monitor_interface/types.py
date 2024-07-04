from dataclasses import dataclass
from .protocols import ConcreteSerialMonitorInterface


@dataclass(frozen=True, slots=True)
class SerialMonitorOptions:
    # required
    interface: ConcreteSerialMonitorInterface
    sample_rate_ms: float
    # has defaults
    timestamp_field_name: str = "time"

    def __post_init__(self):
        if self.sample_rate_ms < 25:
            raise ValueError("sample_rate_ms must be >= 25")
