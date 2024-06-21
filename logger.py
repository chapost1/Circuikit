from env import READINGS_LOG_FILE_PATH
from models import UltrasonicRead
import dataclasses
import json
import os


class ReadingsLogger:
    __slots__ = "readings_descriptor", "flush_counter", "flush_treshold"

    def __init__(self, flush_treshold: int = 100):
        self.flush_counter = 0
        self.flush_treshold = flush_treshold
        self.readings_descriptor = open(READINGS_LOG_FILE_PATH, "a")

    def __destroy__(self):
        self.readings_descriptor.close()

    def on_new_read(self, new_read: UltrasonicRead):
        self.readings_descriptor.write(f"{json.dumps(dataclasses.asdict(new_read))}\n")
        if self.flush_counter == 0:
            self.readings_descriptor.flush()
            os.fsync(self.readings_descriptor)
        self.flush_counter = (self.flush_counter + 1) % self.flush_treshold
