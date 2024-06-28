import subprocess
import signal
import sys
import os
import atexit
import platform


def _get_chrome_application_path() -> str:
    platform_name = platform.system()
    if platform_name == "Darwin":
        # macOS
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif platform_name == "Windows":
        return r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif platform_name == "Linux":
        return "/usr/bin/google-chrome"  # Path to Chrome on Linux, adjust if needed
    else:
        raise NotImplementedError(f"Unsupported platform name={platform_name}")


def open_chrome_process(profile_data_dir: str, debugger_port: int) -> None:
    user_data_dir_absolute_path = os.path.abspath(profile_data_dir)
    CHROME_ARGS = [
        _get_chrome_application_path(),
        f"--remote-debugging-port={debugger_port}",
        f"--user-data-dir={user_data_dir_absolute_path}",
    ]

    # Start Chrome process
    chrome_process = subprocess.Popen(CHROME_ARGS)

    # Register a cleanup function to kill Chrome when Python script exits
    def cleanup():
        try:
            chrome_process.terminate()  # Use terminate() for both Windows and Unix-like systems
            chrome_process.wait(timeout=5)
        except Exception as e:
            print(f"Error terminating Chrome: {e}")

    atexit.register(cleanup)

    # Function to handle termination signals
    def signal_handler(sig, frame):
        cleanup()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
