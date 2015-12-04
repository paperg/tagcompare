import json
from urllib import urlencode
import time

import requests

import settings
import logger


TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")
PL_DOMAIN = settings.DEFAULT.domain
LOGGER = logger.Logger(__name__).get()


def _read_placelocal_api_headers():
    headers = settings.DEFAULT.placelocal['secret']
    return headers


def get_active_campaigns(pid):
    # TODO: Make this better
    url = str.format("https://{}/api/v2/publication/{}/campaigns?status=active",
                     PL_DOMAIN, pid)
    r = requests.get(url, headers=_read_placelocal_api_headers())
    if r.status_code != 200:
        LOGGER.error("getActiveCampaigns %s - API error: %s", url, r)
        return []

    data = json.loads(r.text)
    campaigns = data['data']['campaigns']

    # TODO: There's probably a better way to do this...
    result = []
    for c in campaigns:
        cid = c['id']
        result.append(cid)
    LOGGER.debug("Found %s active campaigns for publisher %s.  IDs: %s",
                 len(campaigns), pid, result)
    return result


def __get_tags(cid):
    """
    Gets a set of tags for a campaign, the key is its size and the value is the tag HTML
    :param cid:
    :return:
    """
    adsizes = ['smartphone_banner', 'skyscraper', 'halfpage',
               'medium_rectangle', 'smartphone_wide_banner',
               'leaderboard']
    # TODO: Support different protocol / tag type
    # protocol = ['http_ad_tags', 'https_ad_tags']
    # type = ['iframe', 'script']
    url = "https://{}/api/v2/campaign/{}/tags?".format(PL_DOMAIN, cid)

    # Animation time is set to 1 to make it static after 1s
    qp = urlencode(
        {"ispreview": 0, "isae": 0, "animationtime": 1, "usetagmacros": 0})
    url += qp
    r = requests.get(url, headers=_read_placelocal_api_headers())
    if r.status_code != 200:
        LOGGER.error("getTags: error: %s", r)
        return None

    try:
        tags_data = json.loads(r.text)['data']['http_ad_tags']
        if not tags_data:
            LOGGER.warning("No tags found for cid %s, tags data: %s", cid,
                           tags_data)
            return None

        result = {}
        for size in adsizes:
            tag = tags_data[size]['iframe']
            assert len(tag) > 0, "No tag data found!"
            LOGGER.debug("size: %s, tag: %s", size, tag)
            result[size] = tag

        LOGGER.debug("result: %s", result)
        return result
    except KeyError as e:
        LOGGER.exception("Missing %s from response!", e)
        return None


def __get_active_tags_for_publisher(pid):
    campaigns = get_active_campaigns(pid)

    if not campaigns:
        return None

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

    LOGGER.info(
        "get_tags_for_campaigns (%s campaigns): %s...  (this might take a while)",
        len(cids), cids)
    if not cids:
        return None

    total_tags = 0
    result = {}
    for cid in cids:
        tags = __get_tags(cid)
        if not tags:
            LOGGER.warn("No tags found for cid %s" % cid)
            continue
        result[cid] = tags
        total_tags += len(tags)
    return result, total_tags


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
