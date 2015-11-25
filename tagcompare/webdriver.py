import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import settings
import image


def _read_remote_webdriver_key():
    data = settings.DEFAULT.webdriver
    return str.format('{}:{}', data['user'], data['key'])


def setup_webdriver(remote=True, capabilities=None):
    if remote:
        if not capabilities:
            raise ValueError("capabilities must be defined for remote runs!")

        remote_webdriver_url = "http://{}@{}".format(
            _read_remote_webdriver_key(), settings.DEFAULT.webdriver['url'])
        driver = webdriver.Remote(
            command_executor=remote_webdriver_url,
            desired_capabilities=capabilities)
    else:
        driver = webdriver.Firefox()

    driver.implicitly_wait(20)
    driver.get("about:blank")
    return driver


def wait_until_element_disappears(driver, locator):
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located(locator=locator))


def _display_tag(driver, tag):
    script = _make_script(tag)
    driver.execute_script(script)

    # Wait until the load spinner goes away
    load_spinner_locator = (By.CSS_SELECTOR, "img[class*='pl-loader-'")
    wait_until_element_disappears(driver=driver, locator=load_spinner_locator)
    time.sleep(3)  # For good measure


def _make_script(tag):
    script = "document.body.innerHTML=\"{}\";".format(tag) \
        .replace('\n', '').replace('\r', '').rstrip()
    # print script
    return script


def screenshot_element(driver, element, output_path):
    """Take a screenshot of a specific webelement
    http://stackoverflow.com/questions/15018372/how-to-take-partial-screenshot-with-selenium-webdriver-in-python
    """
    size = element.size
    location = element.location

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    cropbox = (left, top, right, bottom)

    f = _screenshot(driver, output_path)
    img = image.crop(f, cropbox)
    return img


def _screenshot(driver, output_path):
    if not output_path.endswith('.png'):
        output_path += ".png"
    print "capturing screenshot to {}".format(output_path)
    driver.get_screenshot_as_file(output_path)
    return output_path
