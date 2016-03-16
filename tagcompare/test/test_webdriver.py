import os

import pytest

from tagcompare import webdriver
from tagcompare import settings
from tagcompare.webdriver import WebDriverType


def test_setup_webdriver_exceptions():
    with pytest.raises(ValueError):
        webdriver.setup_webdriver(drivertype=None)
    with pytest.raises(ValueError):
        webdriver.setup_webdriver(drivertype='badtype')
    with pytest.raises(ValueError):
        webdriver.setup_webdriver(drivertype=WebDriverType.REMOTE,
                                  capabilities=None)


def test_phantomjs_screenshot_tag():
    testdriver = webdriver.setup_webdriver(WebDriverType.PHANTOM_JS)
    __test_webdriver_display_tag(testdriver, check_errors=False)
    __test_screenshot_tag(testdriver)
    testdriver.quit()


def test_get_capabilities_for_config():
    config_name = 'chrome'
    caps = webdriver.get_capabilities_for_config(config_name=config_name,
                                                 build='testbuild')
    assert caps['name'] == config_name


@pytest.mark.integration
def test_webdriver_screenshot_tag():
    testcaps = {
        "name": "tagcompare_test",
        "platform": "Windows 7",
        "browserName": "chrome"
    }
    testdriver = webdriver.setup_webdriver(WebDriverType.REMOTE,
                                           capabilities=testcaps)
    __test_webdriver_display_tag(testdriver)
    __test_screenshot_tag(testdriver)
    testdriver.quit()


def __test_screenshot_tag(testdriver):
    tag_element = testdriver.find_element_by_tag_name('iframe')
    screenshot_path = os.path.join(
        settings.Test.TEST_ASSETS_DIR, 'test_screenshot')
    img = webdriver.screenshot_element(driver=testdriver, element=tag_element,
                                       output_path=screenshot_path)
    assert img, "Could not get image from screenshot!"

    # Test that we appended .png to the path and that it exists
    screenshot_path += ".png"
    assert os.path.exists(screenshot_path), \
        "Screenshot was not taken at path: %s" % screenshot_path

    # Cleanup
    os.remove(screenshot_path)


def __test_webdriver_display_tag(testdriver, check_errors=True):
    # The specific tag I'm using will have one browser error in it
    tag_path = os.path.join(settings.Test.TEST_ASSETS_DIR, "test_tag.html")
    with open(tag_path, "r") as tag_file:
        test_pl_tag = tag_file.read()
        errors = webdriver.display_tag(driver=testdriver, tag=test_pl_tag)
        if check_errors:
            assert len(errors) == 1, "We should have found exactly 1 error!"
            assert errors[0][
                'level'] == 'SEVERE', "errors should have SEVERE level!"
