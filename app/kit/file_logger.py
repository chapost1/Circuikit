from app.models import Sensors
from app.kit.task import Task
from pathlib import Path
import dataclasses
import json
import os


class FileLogger(Task):
    def __init__(
        self, file_path: str = "./dirty/logs/readings.txt", flush_treshold: int = 100
    ):
        super().__init__()
        self.flush_counter = 0
        self.flush_treshold = flush_treshold
        output_file = Path(file_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        self.file_descriptor = open(file=file_path, mode="w+")

    def __destroy__(self):
        self.file_descriptor.close()

    def on_message(self, message: Sensors) -> None:
        if self.file_descriptor is None:
            return
        self.file_descriptor.write(f"{json.dumps(dataclasses.asdict(message))}\n")
        if self.flush_counter == 0:
            self.file_descriptor.flush()
            os.fsync(self.file_descriptor)
        self.flush_counter = (self.flush_counter + 1) % self.flush_treshold
