from app.models import Sensors


class ExampleGUI:
    def __init__(self):
        super().__init__()
        # Do something that init screen window

    def update_screen(self, message: Sensors) -> None:
        print("Yo I'm GUI", flush=True)
        # Does something
        pass
