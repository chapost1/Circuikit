from app.models import Sensors
from app.task import Task


class GUI(Task):
    def __init__(self):
        super().__init__()

    def on_message(self, message: Sensors) -> None:
        self.update_screen(message=message)

    def update_screen(self, message: Sensors):
        # Draw to the sceren or something
        pass
