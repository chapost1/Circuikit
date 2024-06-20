from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from models import UltrasonicRead
from typing import Callable
from env import (
    SAMPLE_RATE_MS,
    THINKERCAD_URL,
    DEBUGGER_PORT,
)

def open_simulation() -> WebDriver:
    # Specify the debugging address for the already opened Chrome browser
    debugger_address = f'localhost:{DEBUGGER_PORT}'

    # Set up ChromeOptions and connect to the existing browser
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", debugger_address)

    # Initialize the WebDriver with the existing Chrome instance
    driver = webdriver.Chrome(
        options=chrome_options
    )
    # Now, you can interact with the already opened Chrome browser
    print(f'Driver opens url={THINKERCAD_URL}')
    driver.get(THINKERCAD_URL)
    try:
        WebDriverWait(driver=driver, timeout=10).until(
            EC.presence_of_element_located((By.ID, 'CODE_EDITOR_ID'))
        )
    except:
        print('Failed to load page in specified timeout due to indicator')
        driver.quit()
        exit(1)
    return driver

def is_code_panel_open(driver: WebDriver):
    code_panel = driver.find_element(by=By.CLASS_NAME, value='code_panel')
    code_panel_right_position = code_panel.value_of_css_property(property_name='right')
    return code_panel_right_position == '0px'

def open_code_editor(driver: WebDriver):
    is_open = is_code_panel_open(driver=driver)
    if not is_open:
        open_code_editor_button = driver.find_element(by=By.ID, value='CODE_EDITOR_ID')
        open_code_editor_button.click()
    while not is_open:
        driver.implicitly_wait(0.1)
        is_open = is_code_panel_open(driver=driver)

def open_serial_monitor(driver: WebDriver):
    open_code_editor(driver=driver)
    open_serial_monitor_button = driver.find_element(by=By.ID, value='SERIAL_MONITOR_ID')
    open_serial_monitor_button.click()

def start_simulation(driver: WebDriver):
    start_simulation_button = driver.find_element(by=By.ID, value='SIMULATION_ID')
    start_simulation_button.click()

def sample_serial_monitor(driver: WebDriver, on_new_read: Callable[[list[UltrasonicRead]], None]):
    # so basically serial monitor is bound to max line of 60
    # so reading all of it all the time and take last should be fine as long as
    # the service output in less frequent than the python read rate
    while True:
        serial_content = driver.find_element(by=By.CLASS_NAME, value='code_panel__serial__content__text')
        text = serial_content.get_attribute('innerHTML')
        samples = extract_valid_samples(text)
        on_new_read(samples)
        driver.implicitly_wait(SAMPLE_RATE_MS / 1000)

def extract_valid_samples(data: str):
    samples = []
    lines = data.split('\n')
    for line in lines:
        try:
            sample = UltrasonicRead(**json.loads(line))
            samples.append(sample)
        except ValueError:
            # print(f'faled to load incomplete line={line}')
            # that's expected...
            pass
    return samples

def watch(notify: Callable[[list[UltrasonicRead]], None]):
    driver = open_simulation()
    open_serial_monitor(driver=driver)
    driver.implicitly_wait(1)
    start_simulation(driver=driver)

    last_sample_time = 0

    def on_new_read(new_samples: list[UltrasonicRead]):
        nonlocal last_sample_time
        delta: list[UltrasonicRead] = []
        if len(new_samples) == 0:
            return
        for sample in new_samples:
            if sample.time > last_sample_time:
                delta.append(sample)

        last_sample_time = new_samples[-1].time
        notify(delta)

    sample_serial_monitor(driver=driver, on_new_read=on_new_read)

    # Remember to close the WebDriver when you're done
    driver.quit()
