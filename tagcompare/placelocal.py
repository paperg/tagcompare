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


def __get_route(route, domain=PL_DOMAIN):
    url = str.format("https://{}/{}", domain, route)
    r = requests.get(url, headers=settings.DEFAULT.get_placelocal_headers())
    if r.status_code != 200:
        raise ValueError("GET {} failed with{}".format(route, r.text))
    if 'data' not in r.text:
        raise ValueError("Invalid PL response - no data!")
    return json.loads(r.text)['data']


def __get_active_campaigns(pid):
    route = "api/v2/publication/{}/campaigns?status=active".format(pid)
    data = __get_route(route)
    campaigns = data['campaigns']

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
    route = "api/v2/campaign/{}/tags?".format(cid)

    # Animation time is set to 1 to make it static after 1s
    qp = urlencode(
        {"ispreview": 0, "isae": 0, "animationtime": settings.TAG_ANIMATION_TIME,
         "usetagmacros": 0})
    route += qp
    data = __get_route(route)
    if not data:
        LOGGER.warning("No tags found for cid %s, tags data: %s", cid,
                       data)
        return None

    tags_data = data['http_ad_tags']
    if not isinstance(tags_data, dict):
        raise ValueError("tag_data is not a dict!:\n %s", tags_data)
    # LOGGER.debug("__get_tags result:\n%s\n\n\n", tags_data)
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


def _get_pids_from_publisher(pid):
    if not pid:
        raise ValueError("Invalid publisher id!")
    route = "api/v2/publisher/{}/publications".format(pid)
    data = __get_route(route)
    if not data:
        return None

    publications = data['publications']
    pids = []
    for p in publications:
        pids.append(p['id'])
    return pids


def _get_all_pids(pids):
    """
    Expand potential super publishers to get publishers from them
    :param pids:
    :return:
    """
    all_pids = []
    for pid in pids:
        newpids = _get_pids_from_publisher(pid)
        if not newpids:
            all_pids.append(pid)
        else:
            all_pids += newpids
    result = list(set(all_pids))  # unique list
    LOGGER.debug("_get_all_pids: %s", result)
    return result


def get_cids(cids=None, pids=None):
    """
    Gets a list of campaign ids from a combinination of cids and pids
    :param cids: campaign ids, directly gets appended to the list of cids
    :param pids: publisher or superpub ids, this is confusing - I know
    :return: a list of campaign ids
    """
    if not pids:
        if cids:
            return cids
        raise ValueError("pid must be specified if there are no cids!")

    if pids and not cids:
        cids = []
    all_pids = _get_all_pids(pids)
    for pid in all_pids:
        new_cids = __get_active_campaigns(pid)
        if new_cids:
            cids += new_cids
    return cids
