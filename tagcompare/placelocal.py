from multiprocessing.pool import ThreadPool
import json
from urllib import urlencode
import time

import requests

import settings
import logger

TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")
LOGGER = logger.Logger(__name__).get()

# TODO: Objectify - domain be made into a field


def __get_route(route, domain=None):
    if not domain:
        domain = settings.DEFAULT.domain

    url = str.format("https://{}/{}", domain, route)
    r = requests.get(url, headers=settings.DEFAULT.get_placelocal_headers())
    assert r.status_code == 200, "GET {} failed with{}".format(route, r.text)
    assert 'data' in r.text, "Invalid PL response - no data!"
    return json.loads(r.text)['data']


def __get_active_campaigns(pid, domain=None):
    route = "api/v2/publication/{}/campaigns?status=active".format(pid)
    data = __get_route(route, domain)
    campaigns = data['campaigns']

    result = []
    for c in campaigns:
        cid = c['id']
        result.append(cid)
    LOGGER.debug("Found %s active campaigns for publisher %s.  IDs: %s",
                 len(campaigns), pid, result)
    return result


def __get_tags(cid, ispreview=1, domain=None):
    """
    Gets a set of tags for a campaign,
    the key is its size and the value is the tag HTML
    :param cid: the campaign id
    :param ispreview: preview tags don't generate tracking traffic
    :return: tags data for all the tags of a given cid
    """
    # TODO: Support different protocols
    # protocol = ['http_ad_tags', 'https_ad_tags']
    route = "api/v2/campaign/{}/tags?".format(cid)

    # Animation time is set to 1 to make it static after 1s
    qp = urlencode(
        {"ispreview": ispreview, "isae": 0, "animationtime": settings.TAG_ANIMATION_TIME,
         "usetagmacros": 0})
    route += qp
    data = __get_route(route, domain)
    if not data:
        LOGGER.warning("No tags found for cid %s, tags data: %s", cid,
                       data)
        return None

    tags_data = data['http_ad_tags']
    return tags_data


def get_tags_for_campaigns(cids, ispreview=0, domain=None):
    """
    Gets a set of tags for multiple campaigns:

    :param cids: a list of campaign ids
    :param ispreview: change to 1 to get preview tags, 0 by default
    :return: a dictionary of tags with the cid as key
    """
    if not domain:
        domain = settings.DEFAULT.domain

    if not cids:
        raise ValueError("cids not defined!")
    LOGGER.debug(
        "Get tags for %s campaigns: %s...", len(cids), cids)

    tp = ThreadPool(processes=10)
    results = {}
    for cid in cids:
        results[cid] = tp.apply_async(func=__get_tags,
                                      args=(cid, ispreview, domain))
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


def get_cids_from_settings(settings_obj=settings.DEFAULT):
    cids = settings_obj.campaigns
    pids = settings_obj.publishers
    return _get_cids(cids, pids)


def _get_cids(cids=None, pids=None):
    """
    Gets a list of campaign ids from a combinination of cids and pids
    :param cids: campaign ids, directly gets appended to the list of cids
    :param pids: publisher or superpub ids, this is confusing - I know
    :return: a list of campaign ids
    """
    if cids:
        return cids

    if not pids:
        raise ValueError("pids must be specified if there are no cids!")

    cids = []
    all_pids = _get_all_pids(pids)
    for pid in all_pids:
        new_cids = __get_active_campaigns(pid)
        if new_cids:
            cids += new_cids
    return cids
