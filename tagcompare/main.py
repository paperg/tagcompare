import placelocal
import webdriver
import settings
import output
import compare


# TODO: Globals should get refactored into a settings file
# How long to wait for ad to load in seconds
WAIT_TIME_PER_AD = 7

# https://www.browserstack.com/automate/capabilities
BROWSER_CONFIGS = settings.DEFAULT.configs


def testcampaign(cid):
    tags = {}
    tags_per_campaign = placelocal.get_tags(cid=cid)
    if not tags_per_campaign:
        print "No tags found for campaign {}, bailing...".format(cid)
        return

    tags[cid] = tags_per_campaign

    # Use remote browsers
    configs = []
    for config in BROWSER_CONFIGS:
        config_data = BROWSER_CONFIGS[config]
        if not config_data['enabled']:
            continue

        configs.append(config)
        capabilities = config_data['capabilities']
        pathbuilder = output.PathBuilder(config=config, cid=cid)
        webdriver.capture_tags_remotely(capabilities, tags, pathbuilder)

    compare.compare_output(output.PathBuilder(cid=cid), configs=configs)


def main(cids=None, pid=None):
    # Input is a PID (publisher id) or a list of CIDs (campaign Ids)
    if not cids:
        if not pid:
            raise ValueError("pid must be specified if there are no cids!")
        cids = placelocal.get_active_campaigns(pid)

    for cid in cids:
        testcampaign(cid)


if __name__ == '__main__':
    main(cids=settings.DEFAULT.campaigns, pid=settings.DEFAULT.publishers)
