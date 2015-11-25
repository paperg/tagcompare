import json
from urllib import urlencode
import time

import requests

import settings


TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")
PL_DOMAIN = settings.DEFAULT.domain


def _read_placelocal_api_headers():
    headers = settings.DEFAULT.placelocal['secret']
    return headers


def get_active_campaigns(pid):
    # TODO: Make this better
    url = str.format("https://{}/api/v2/publication/{}/campaigns?status=active", PL_DOMAIN, pid)
    r = requests.get(url, headers=_read_placelocal_api_headers())
    if r.status_code != 200:
        print("getActiveCampaigns {} - API error: {}".format(url, r))
        return None

    data = json.loads(r.text)
    campaigns = data['data']['campaigns']

    # TODO: There's probably a better way to do this...
    result = []
    for c in campaigns:
        cid = c['id']
        result.append(cid)
    print "Found {} active campaigns for publisher {}.  IDs: {}".format(len(campaigns), pid, result)
    return result


# Gets a set of tags for a campaign, the key is its size and the value is the tag HTML
def __get_tags(cid):
    adsizes = ['smartphone_banner', 'skyscraper', 'halfpage', 'medium_rectangle', 'smartphone_wide_banner',
               'leaderboard']
    protocol = ['http_ad_tags', 'https_ad_tags']
    type = ['iframe', 'script']

    # TODO: hardcoding config params is bad
    url = "https://{}/api/v2/campaign/{}/tags?".format(PL_DOMAIN, cid)

    # TODO: Note that animation time is set to 1 to make it static after 1s, but we only get last frame
    qp = urlencode({"ispreview": 0, "isae": 0, "animationtime": 1, "usetagmacros": 0})
    url += qp
    r = requests.get(url, headers=_read_placelocal_api_headers())
    if r.status_code != 200:
        print("getTags: error: %s" % r)
        return None

    try:
        tags_data = json.loads(r.text)['data']['http_ad_tags']
        if not tags_data:
            print("No tags found for cid {}, tags data: {}".format(cid, tags_data))
            return None

        result = {}
        for size in adsizes:
            # print 'size: %s' % size
            tag = tags_data[size]['iframe']
            assert len(tag) > 0, "No tag data found!"
            # print tag
            result[size] = tag

        # print "result: " + str(result)
        return result
    except KeyError as e:
        print "missing %s from response!" % (e, )
        return None


def __get_active_tags_for_publisher(pid):
    campaigns = get_active_campaigns(pid)

    if not campaigns:
        return None

    # print dir(campaigns)
    all_tags = {}
    for c in campaigns:
        cid = c['id']
        tags = __get_tags(cid)
        all_tags[cid] = tags

    return all_tags


def get_tags_for_campaigns(cids):
    """
    Gets a set of tags for multiple campaigns in this form:

    tags = {
        "cid1": {
            "size1": "<tag>html</tag>",
            "size2": "<tag>html</tag>"...
        },
        "cid2": {...
        }...
    }
    :param cids:
    :return:
    """

    if not cids:
        return None

    result = {}
    for cid in cids:
        result[cid] = __get_tags(cid)
    return result


def get_cids(cids=None, pids=None):
    # Input is a PID (publisher id) or a list of CIDs (campaign Ids)
    if not cids:
        if not pids:
            raise ValueError("pid must be specified if there are no cids!")

        cids = []
        for pid in pids:
            new_cids = get_active_campaigns(pid)
            if new_cids:
                cids += new_cids
    return cids


# TODO: Make test for this
def test():
    all_tags = __get_active_tags_for_publisher()
    tag_count = len(all_tags)
    print "getActiveTagsForPublisher_test: Found {} tags".format(tag_count)
    assert tag_count > 0, "No tags found!"


if __name__ == '__main__':
    test()
