from .models import Sensors
import dataclasses
import json
import os


class ReadingsLogger:
    __slots__ = "skip_logging", "readings_descriptor", "flush_counter", "flush_treshold"

    def __init__(self, file_path: str, flush_treshold: int = 100):
        self.flush_counter = 0
        self.flush_treshold = flush_treshold
        self.skip_logging = file_path == ""
        if self.skip_logging:
            print(
                "[ReadingsLogger] No READINGS_LOG_FILE_PATH, going to skip logging",
                flush=True,
            )
        else:
            self.readings_descriptor = open(file_path, "a")

    def __destroy__(self):
        self.readings_descriptor.close()

    def on_new_read(self, new_read: Sensors):
        if self.skip_logging:
            return
        self.readings_descriptor.write(f"{json.dumps(dataclasses.asdict(new_read))}\n")
        if self.flush_counter == 0:
            self.readings_descriptor.flush()
            os.fsync(self.readings_descriptor)
        self.flush_counter = (self.flush_counter + 1) % self.flush_treshold
