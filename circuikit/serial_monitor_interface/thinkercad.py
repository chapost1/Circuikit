from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
import logging

LOGGER.setLevel(logging.WARNING)
from .chrome_process import open_chrome_process


def open_simulation(
    thinkercad_url: str,
    debugger_port: int,
    open_simulation_timeout: int,
    chrome_profile_path: str | None,
) -> WebDriver:
    open_chrome_process(
        profile_data_dir=chrome_profile_path, debugger_port=debugger_port
    )

    # Specify the debugging address for the already opened Chrome browser
    debugger_address = f"localhost:{debugger_port}"

    # Set up ChromeOptions and connect to the existing browser
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", debugger_address)

    # Initialize the WebDriver with the existing Chrome instance
    driver = webdriver.Chrome(options=chrome_options)
    # Now, you can interact with the already opened Chrome browser
    print(f"Driver opens url={thinkercad_url}")
    driver.get(thinkercad_url)
    try:
        WebDriverWait(driver=driver, timeout=open_simulation_timeout).until(
            EC.presence_of_element_located((By.ID, "CODE_EDITOR_ID"))
        )
    except:
        print("Failed to load page in specified timeout due to indicator")
        driver.quit()
        exit(1)
    return driver


def is_code_panel_open(driver: WebDriver) -> bool:
    code_panel = driver.find_element(by=By.CLASS_NAME, value="code_panel")
    code_panel_right_position = code_panel.value_of_css_property(property_name="right")
    return code_panel_right_position == "0px"


def open_code_editor(driver: WebDriver) -> None:
    is_open = is_code_panel_open(driver=driver)
    if not is_open:
        open_code_editor_button = driver.find_element(by=By.ID, value="CODE_EDITOR_ID")
        open_code_editor_button.click()
    while not is_open:
        driver.implicitly_wait(0.1)
        is_open = is_code_panel_open(driver=driver)


def open_serial_monitor(driver: WebDriver) -> None:
    open_code_editor(driver=driver)
    open_serial_monitor_button = driver.find_element(
        by=By.ID, value="SERIAL_MONITOR_ID"
    )
    open_serial_monitor_button.click()


def start_simulation(driver: WebDriver) -> None:
    start_simulation_button = driver.find_element(by=By.ID, value="SIMULATION_ID")
    start_simulation_button.click()


def sample_serial_monitor(
    driver: WebDriver,
) -> str | None:
    # so basically serial monitor is bound to max line of 60
    # so reading all of it all the time and take last should be fine as long as
    # the service output in less frequent than the python read rate
    serial_content = driver.find_element(
        by=By.CLASS_NAME, value="code_panel__serial__content__text"
    )
    if serial_content is None:
        return None
    text = serial_content.get_attribute("innerHTML")
    if text is None:
        print("serial monitor text is None")
        return None
    return text


def speak_with_serial_monitor(driver: WebDriver, message: str) -> None:
    serial_input = driver.find_element(
        by=By.CLASS_NAME, value="code_panel__serial__input"
    )
    if serial_input is None:
        print("[ERROR] cannot find serial input")
        return
    serial_input.send_keys(message)
    serial_input.send_keys(Keys.ENTER)


class ThinkercadInterface:
    __slots__ = (
        "debugger_port",
        "thinkercad_url",
        "chrome_profile_path",
        "open_simulation_timeout",
        "driver",
    )

    def __init__(
        self,
        thinkercad_url: str,
        chrome_profile_path: str | None = None,
        debugger_port: int = 8989,
        open_simulation_timeout: int = 10,
    ):
        self.thinkercad_url = thinkercad_url
        self.debugger_port = debugger_port
        self.chrome_profile_path = chrome_profile_path
        self.open_simulation_timeout = open_simulation_timeout

    def __destroy__(self):
        self.stop()

    def _init_simulation(self) -> None:
        self.driver = open_simulation(
            thinkercad_url=self.thinkercad_url,
            debugger_port=self.debugger_port,
            chrome_profile_path=self.chrome_profile_path,
            open_simulation_timeout=self.open_simulation_timeout,
        )
        open_serial_monitor(driver=self.driver)
        start_simulation(driver=self.driver)
        self.driver.implicitly_wait(1)

    def send_message(self, message: str) -> None:
        if self.driver is None:
            print("[SeleniumInterface] Driver is not running. send_message is rejected")
            return
        speak_with_serial_monitor(driver=self.driver, message=message)

    def sample(self) -> str | None:
        if self.driver is None:
            print("[SeleniumInterface] Driver is not running. send_message is rejected")
            return
        return sample_serial_monitor(driver=self.driver)

    def start(self) -> None:
        self._init_simulation()

    def stop(self) -> None:
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
