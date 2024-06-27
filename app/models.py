from dataclasses import dataclass


@dataclass(frozen=True)
class Sensors:
    time: int
    some_key: int
