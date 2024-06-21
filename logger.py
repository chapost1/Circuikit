from env import READINGS_LOG_FILE_PATH
from models import UltrasonicRead
import dataclasses
import json


class ReadingsLogger:
    __slots__ = "readings_descriptor"

    def __init__(self):
        self.readings_descriptor = open(READINGS_LOG_FILE_PATH, "a")

    def __destroy__(self):
        self.readings_descriptor.close()

    def on_new_read(self, new_read: UltrasonicRead):
        self.readings_descriptor.write(f"{json.dumps(dataclasses.asdict(new_read))}\n")
