import logging

logging.basicConfig(level=logging.WARNING)

if __name__ == "__main__":
    # from thinkercad_to_custom_ui.example import run_example
    from thinkercad_to_thingsboard.example import run_example
    from serial_port_to_print.example import run_example

    run_example()
