import os
import time
import image
import placelocal
import browser

# TODO: Globals should get refactored into a config file
# How long to wait for ad to load in seconds
WAIT_TIME_PER_AD = 7

TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")
OUTPUT_DIR = os.path.join("output", TIMESTAMP)

# https://www.browserstack.com/automate/capabilities
BROWSER_TEST_MATRIX = {
    "chrome": {
        'platform': "WINDOWS",
        'browserName': "chrome",
        'browserstack.debug:': "true",
        'project': "advers",
        'name': TIMESTAMP,
        'browserstack.selenium_version': "2.48.2"
    },
    "firefox": {
        'platform': "WINDOWS",
        'browserName': "firefox",
        'browserstack.debug:': "true",
        'project': "advers",
        'name': TIMESTAMP,
        'browserstack.selenium_version': "2.48.2"
    },
    "ie11": {
        'platform': "WINDOWS",
        'browserName': "internet explorer",
        'version': "11",
        'browserstack.debug:': "true",
        'project': "advers",
        'name': TIMESTAMP,
        'browserstack.selenium_version': "2.48.2"
    }
}


def testcampaign(cid):
    tags = {}
    tags[cid] = placelocal.get_tags(cid=cid)
    if not tags:
        print "No tags found, bailing..."
        return

    # Use remote browsers from browserstack
    for config in BROWSER_TEST_MATRIX:
        capabilities = BROWSER_TEST_MATRIX[config]
        output_dir = os.path.join(OUTPUT_DIR, config)
        browser.capture_tags_remotely(capabilities, tags, output_dir)

    image.compare_output_dir(OUTPUT_DIR)


def main(cids=None, pid=None):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Input is a PID (pubilsher id) or a list of CIDs (campaign Ids)
    if not cids:
        if not pid:
            raise ValueError("pid must be specified if there are no cids!")

        cids = placelocal.get_active_campaigns(pid)

    for cid in cids:
        testcampaign(cid)


if __name__ == '__main__':
    main(cids=[4795])
