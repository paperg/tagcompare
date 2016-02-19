import time

from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import settings
import image
import logger

LOGGER = logger.Logger(name=__name__).get()


def setup_webdriver(capabilities):
    driver = __setup_remote_webdriver(capabilities=capabilities)
    driver.implicitly_wait(20)
    return driver


def get_capabilities_for_config(config_name, build, max_duration=3600,
                                all_configs=None):
    if not all_configs:
        all_configs = settings.DEFAULT.all_configs
    assert config_name in all_configs, 'configname not in all_configs!'
    config_data = all_configs[config_name]
    assert config_data['enabled'], 'config not enabled!'
    capabilities = config_data['capabilities']
    capabilities['name'] = config_name
    capabilities['build'] = build
    capabilities['maxDuration'] = max_duration
    return capabilities


def __setup_remote_webdriver(capabilities):
    if not capabilities:
        raise ValueError("capabilities must be defined for remote runs!")

    # Update capabilities
    capabilities['public'] = 'share'
    user = settings.DEFAULT.get_saucelabs_user()
    key = settings.DEFAULT.get_saucelabs_key()
    remote_webdriver_url = "http://{}:{}@ondemand.saucelabs.com:80/wd/hub".format(
        user, key)
    driver = webdriver.Remote(
        command_executor=remote_webdriver_url,
        desired_capabilities=capabilities)
    remote_url = "http://www.saucelabs.com/jobs/%s" % driver.session_id
    LOGGER.debug("Starting remote webdriver job: %s\n%s",
                 remote_url, capabilities)
    return driver


def check_browser_logs(driver):
    """
    Checks browser for errors, returns a list of errors
    This only works for Chrome
    :param driver:
    :return:
    """
    try:
        browserlogs = driver.get_log('browser')
    except (ValueError, WebDriverException) as e:
        LOGGER.debug("Could not get browser logs for driver %s due to exception: %s",
                     driver, e)
        return []

    errors = []
    for entry in browserlogs:
        if entry['level'] == 'SEVERE':
            errors.append(entry)
    return errors


def wait_until_element_disappears(driver, locator):
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located(locator=locator))


def display_tag(driver, tag, wait_for_load=True, wait_time=3):
    driver.get("about:blank")  # Clear the page first
    script = _make_script(tag)
    driver.execute_script(script)

    if wait_for_load:
        # TODO: implementation is specific to PaperG creatives
        # Wait until the load spinner goes away
        load_spinner_locator = (By.CSS_SELECTOR, "img[class*='pl-loader-'")
        wait_until_element_disappears(driver=driver,
                                      locator=load_spinner_locator)

        # Account for animation time and add some buffer for good measure
        time.sleep(settings.TAG_ANIMATION_TIME)
        time.sleep(wait_time)

    errors = check_browser_logs(driver)
    return errors


def _make_script(tag):
    script = "document.body.innerHTML=\"{}\";".format(tag) \
        .replace('\n', '').replace('\r', '').rstrip()
    LOGGER.debug("_make_script: %s", script)
    return script


def screenshot_element(driver, element, output_path):
    """Take a screenshot of a specific webelement
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
    LOGGER.debug("capturing screenshot to %s", output_path)
    driver.get_screenshot_as_file(output_path)
    return output_path
