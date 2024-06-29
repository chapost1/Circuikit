from .service import Service
from pathlib import Path
import json
import os


class FileLogger(Service):
    def __init__(self, file_path: str, flush_treshold: int = 100):
        super().__init__()
        self.flush_counter = 0
        self.flush_treshold = flush_treshold
        self.file_path = file_path

    def __destroy__(self):
        self.file_descriptor.close()

    def start(self):
        super().start()
        # opens file desciptor only on start so class will be picklable if not started yet
        output_file = Path(self.file_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        self.file_descriptor = open(file=self.file_path, mode="w+")

    def on_message(self, message: dict) -> None:
        if self.file_descriptor is None:
            return
        self.file_descriptor.write(f"{json.dumps(message)}\n")
        if self.flush_counter == 0:
            self.file_descriptor.flush()
            os.fsync(self.file_descriptor)
        self.flush_counter = (self.flush_counter + 1) % self.flush_treshold
