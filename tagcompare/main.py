import os
import time
import compare
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
        "enabled": False,
        "capabilities": {
            'platform': "WINDOWS",
            'browserName': "chrome",
            'browserstack.debug:': "true",
            'project': "advers",
            'name': TIMESTAMP,
            'browserstack.selenium_version': "2.48.2"
        }
    },
    "firefox41": {
        "enabled": True,
        "capabilities": {
            'platform': "WINDOWS",
            'browserName': "firefox",
            "version": "41",
            'browserstack.debug:': "true",
            'project': "advers",
            'name': TIMESTAMP,
            'browserstack.selenium_version': "2.48.2"
        }
    },
    "firefox": {
        "enabled": True,
        "capabilities": {
            'platform': "WINDOWS",
            'browserName': "firefox",
            'browserstack.debug:': "true",
            'project': "advers",
            'name': TIMESTAMP,
            'browserstack.selenium_version': "2.48.2"
        }
    },
    "ie11": {
        "enabled": False,
        "capabilities": {
            'platform': "WINDOWS",
            'browserName': "internet explorer",
            'version': "11",
            'browserstack.debug:': "true",
            'project': "advers",
            'name': TIMESTAMP,
            'browserstack.selenium_version': "2.48.2"
        }
    }
}


def testcampaign(cid):
    tags = {}
    tags[cid] = placelocal.get_tags(cid=cid)
    if not tags:
        print "No tags found, bailing..."
        return

    # Use remote browsers from browserstack
    configs = []
    for config in BROWSER_TEST_MATRIX:
        config_data = BROWSER_TEST_MATRIX[config]
        if not config_data['enabled']:
            continue

        configs.append(config)
        capabilities = config_data['capabilities']
        output_dir = os.path.join(OUTPUT_DIR, config)
        browser.capture_tags_remotely(capabilities, tags, output_dir)

    compare.compare_output(OUTPUT_DIR, configs=configs)


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
