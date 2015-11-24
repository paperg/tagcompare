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


def testcampaign(cid, pathbuilder):
    tags = {}
    tags_per_campaign = placelocal.get_tags(cid=cid)
    if not tags_per_campaign:
        print "No tags found for campaign {}, bailing...".format(cid)
        return

    tags[cid] = tags_per_campaign
    print "Found {} tags for campaign {}".format(len(tags_per_campaign), cid)

    # Use remote browsers
    configs = []
    for config in BROWSER_CONFIGS:
        config_data = BROWSER_CONFIGS[config]
        if not config_data['enabled']:
            continue

        configs.append(config)
        capabilities = config_data['capabilities']
        pathbuilder.config = config
        pathbuilder.cid = cid
        webdriver.capture_tags_remotely(capabilities, tags, pathbuilder)

    output.aggregate()
    compare.compare_configs(pathbuilder=pathbuilder, configs=configs)


def get_cids(cids=None, pids=None):
    # Input is a PID (publisher id) or a list of CIDs (campaign Ids)
    if not cids:
        if not pids:
            raise ValueError("pid must be specified if there are no cids!")

        cids = []
        for pid in pids:
            new_cids = placelocal.get_active_campaigns(pid)
            if new_cids:
                cids += new_cids
    return cids


def main(cids=None, pids=None):
    # Input is a PID (publisher id) or a list of CIDs (campaign Ids)
    build = output.generate_build_string()
    pathbuilder = output.PathBuilder(build=build)
    cids = get_cids(cids=cids, pids=pids)
    print "Capturing tags for {} campaigns".format(len(cids))
    for cid in cids:
        testcampaign(cid=cid, pathbuilder=pathbuilder)


if __name__ == '__main__':
    main(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
