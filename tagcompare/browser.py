import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import image
import datetime


def setup_webdriver(remote=False, capabilities=None):
    if remote:
        if not capabilities:
            raise ValueError("capabilities must be defined for remote runs!")

        remote_webdriver_url = "http://paperg:CzSxxSypfJKmTHZfyxyg@hub.browserstack.com:80/wd/hub"
        driver = webdriver.Remote(
            command_executor=remote_webdriver_url,
            desired_capabilities=capabilities)
    else:
        # TODO: More configs
        driver = webdriver.Firefox()

    driver.implicitly_wait(20)
    driver.get("about:blank");
    return driver


def wait_until_element_disappears(driver, locator):
    #print("wait_until_element_disappears start... {}".format(datetime.datetime.now()))
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located(locator=locator))
    #print("wait_until_element_disappears end... {}".format(datetime.datetime.now()))

    '''Hack to make it work for IE9
    But it didnt work... so commenting it out:
    browsername = driver.capabilities['browserName']
    if browsername == "internet explorer":
        # IE sucks
        time.sleep(15)
    '''

def _display_tag(driver, tag):
    script = _make_script(tag)
    driver.execute_script(script)

    '''
    Waiting a good amount of time to be sure the ad loaded and reached final state
    TODO: Make the wait smarter by waiting on the loading spinner to go away
    HTML for that element looks like:

    body > div > img.pl-loader-974f3d80-bb74-11e3-a5e2-0800200c9a66

    '''
    load_spinner_locator = (By.CSS_SELECTOR, "img[class*='pl-loader-'")
    wait_until_element_disappears(driver=driver, locator=load_spinner_locator)


def _make_script(tag):
    script = "document.body.innerHTML=\"{}\";".format(tag) \
        .replace('\n', '').replace('\r', '').rstrip()
    # print script
    return script


def _write_html(tag_html, output_path):
    if not output_path.endswith('.html'):
        output_path += ".html"

    with open(output_path, 'w') as f:
        f.write(tag_html)


def _capture_tags(driver, tags, outputdir):
    for cid in tags:
        tags_per_campaign = tags[cid]
        # TODO: Capture all sizes instead of just one
        # print "debug: " + str(tags_per_campaign)
        # for tag_size in tags_per_campaign:
        tag_size = 'medium_rectangle'
        tag_html = tags_per_campaign[tag_size]
        _display_tag(driver, tag_html)

        # Getting ready to write to files
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        tag_label = str("{}-{}").format(cid, tag_size)
        output_path = os.path.join(outputdir, tag_label)

        # TODO: Only works for iframe tags atm
        tag_element = driver.find_element_by_tag_name('iframe')
        screenshot_element(driver, tag_element, output_path)
        _write_html(tag_html=tag_html, output_path=output_path)
        # break  # TODO: Remove


'''
Take a screenshot of a specific webelement
http://stackoverflow.com/questions/15018372/how-to-take-partial-screenshot-with-selenium-webdriver-in-python
'''
def screenshot_element(driver, element, output_path):
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


def capture_tags_remotely(capabilities, tags, outputdir):
    print "Starting browser with capabilities: {}...".format(capabilities)
    driver = setup_webdriver(remote=True, capabilities=capabilities)

    try:
        _capture_tags(driver, tags, outputdir)
    # Catching generics here because we don't want to leak a browser
    except Exception as e:
        print "Exception caught while running display_tags: {}\n{}".format(e, traceback.format_exc())
    finally:
        # Make sure to always close the browser
        driver.quit()
