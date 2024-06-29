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


def _get_user_data_dir_absolute_path(profile_data_dir: str | None) -> str:
    if profile_data_dir is None:
        # Use default
        dirname = os.path.dirname(__file__)
        dir_path = os.path.join(dirname, "__cached-chrome-profile")
        user_data_dir_absolute_path = dir_path
    else:
        user_data_dir_absolute_path = profile_data_dir

    return os.path.abspath(user_data_dir_absolute_path)


def open_chrome_process(debugger_port: int, profile_data_dir: str | None) -> None:
    user_data_dir_absolute_path = _get_user_data_dir_absolute_path(
        profile_data_dir=profile_data_dir
    )
    chrome_args = [
        _get_chrome_application_path(),
        f"--remote-debugging-port={debugger_port}",
        f"--user-data-dir={user_data_dir_absolute_path}",
    ]

    # Start Chrome process
    chrome_process = subprocess.Popen(args=chrome_args)

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
