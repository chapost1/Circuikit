from dataclasses import dataclass


@dataclass(frozen=True)
class UltrasonicRead:
    time: int
    some_key: int
