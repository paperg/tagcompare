from multiprocessing.pool import ThreadPool
import json
from urllib import urlencode
import time
import hashlib

import requests

import settings
import logger


TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")
PL_DOMAIN = settings.DEFAULT.domain
LOGGER = logger.Logger(__name__).get()


def __get_active_campaigns(pid):
    url = str.format(
        "https://{}/api/v2/publication/{}/campaigns?status=active",
        PL_DOMAIN, pid)
    r = requests.get(url, headers=settings.DEFAULT.get_placelocal_headers())
    if r.status_code != 200:
        LOGGER.error("getActiveCampaigns error: %s", r.text)
        return []

    data = json.loads(r.text)
    campaigns = data['data']['campaigns']

    result = []
    for c in campaigns:
        cid = c['id']
        result.append(cid)
    LOGGER.debug("Found %s active campaigns for publisher %s.  IDs: %s",
                 len(campaigns), pid, result)
    return result


def get_campaign_preview_url(cid, size):
    """
    Go to the un tbs'ed ad for a size, it only renders as <script>
    :param cid:
    :param size:
    :return:
    """
    clearance = __make_clearance(cid)
    animation_time = 0

    # This route needs the correct dimension/size name to render
    if "medium_rectangle" in size:
        size = "rectangle"
    elif "smartphone_wide" in size:
        size = "mobile"
    elif "smartphone_banner" in size:
        size = "mobile2"

    url = str.format("http://{}/v3/templates?" +
                     "&optimized=true&playing=true&assetsEnabled=true" +
                     "&clearance={}&size={}&animationTime={}&id={}",
                     PL_DOMAIN, clearance, size, animation_time, cid)
    return url


def __make_clearance(cid):
    clearance = hashlib.md5(cid).hexdigest()
    return clearance[0:6]


def __get_tags(cid):
    """
    Gets a set of tags for a campaign,
    the key is its size and the value is the tag HTML
    :param cid:
    :return:
    """
    # TODO: Support different protocols
    # protocol = ['http_ad_tags', 'https_ad_tags']
    url = "https://{}/api/v2/campaign/{}/tags?".format(PL_DOMAIN, cid)

    # Animation time is set to 1 to make it static after 1s
    qp = urlencode(
        {"ispreview": 0, "isae": 0, "animationtime": settings.TAG_ANIMATION_TIME,
         "usetagmacros": 0})
    url += qp
    r = requests.get(url, headers=settings.DEFAULT.get_placelocal_headers())
    if r.status_code != 200:
        LOGGER.error("getTags error: %s", r.text)
        return None

    tags_data = json.loads(r.text)['data']['http_ad_tags']
    if not tags_data:
        LOGGER.warning("No tags found for cid %s, tags data: %s", cid,
                       tags_data)
        return None

    if not isinstance(tags_data, dict):
        raise ValueError("tag_data is not a dict!:\n %s", tags_data)
    LOGGER.debug("__get_tags result:\n%s\n\n\n", tags_data)
    return tags_data


def get_tags_for_campaigns(cids):
    """
    Gets a set of tags for multiple campaigns:

    :param cids: a list of campaign ids
    :return:
    """
    if not cids:
        raise ValueError("cids not defined!")
    LOGGER.info(
        "get tags for %s campaigns: %s...", len(cids), cids)

    tp = ThreadPool(processes=10)
    results = {}
    for cid in cids:
        results[cid] = tp.apply_async(func=__get_tags, args=(cid,))
    all_tags = {}
    for cid in results:
        tags = results[cid].get()
        if not tags:
            LOGGER.warn("No tags found for cid %s" % cid)
            continue
        all_tags[cid] = tags
    LOGGER.debug("get_tags_for_campaigns for cids=%s returned:\n%s",
                 cids, all_tags)
    return all_tags


def get_cids(cids=None, pids=None):
    # Input is a PID (publisher id) or a list of CIDs (campaign Ids)
    if not cids:
        if not pids:
            raise ValueError("pid must be specified if there are no cids!")

        cids = []
        for pid in pids:
            new_cids = __get_active_campaigns(pid)
            if new_cids:
                cids += new_cids
    return cids
