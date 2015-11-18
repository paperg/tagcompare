import json
from urllib import urlencode
import time
import requests

# TODO: Should get our own secret
# TODO: Put it in from secret file
PL_API_HEADERS = {"pl-secret": "HELLO",
                  "pl-service-identifier": "WORLD"}

PL_TEST_PUBLISHER = "627" # IHG!!
TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")

#PL_DOMAIN = "www.placelocal.com/"
PL_DOMAIN = "www.placelocaldemo.com/"

def getActiveCampaigns(pid=PL_TEST_PUBLISHER):
    # TODO: Make this better
    url = "https://" + PL_DOMAIN + PL_TEST_PUBLISHER + \
          "/campaigns?status=active"
    r = requests.get(url, headers=PL_API_HEADERS)
    if r.status_code != 200:
        print("getActiveCampaigns: Error code: %s" % r.status_code)
        return None

    data = json.loads(r.text)
    #print data
    return data['data']['campaigns']


def getActiveTagsForPublisher(pid=PL_TEST_PUBLISHER):
    campaigns = getActiveCampaigns()

    if not campaigns:
        return None

    #print dir(campaigns)
    all_tags = {}
    for c in campaigns:
        cid = c['id']
        tags = getTags(cid)
        all_tags[cid] = tags

    return all_tags


"""
Gets a set of tags for a campaign, the key is its size and the value is the tag HTML
"""
def getTags(cid):
    adsizes = [ 'smartphone_banner', 'skyscraper', 'halfpage', 'medium_rectangle', 'smartphone_wide_banner', 'leaderboard']
    protocol = ['http_ad_tags', 'https_ad_tags']
    type = ['iframe', 'script']

    # TODO: hardcoding config params is bad
    url = "https://" + PL_DOMAIN + "api/v2/campaign/%s/tags?" % (str(cid))

    # TODO: Note that animation time is set to 1 to make it static after 1s, but we only get last frame
    qp = urlencode({"ispreview": 0, "isae": 0, "animationtime": 1, "usetagmacros": 0})
    url += qp
    r = requests.get(url, headers=PL_API_HEADERS)
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
            #print 'size: %s' % size
            tag = tags_data[size]['iframe']
            assert len(tag) > 0, "No tag data found!"
            #print tag
            result[size] = tag

        #print "result: " + str(result)
        return result
    except KeyError as e:
        print "missing %s from response!" % (e, )
        return None

def getActiveTagsForPublisher_test():
    all_tags = getActiveTagsForPublisher()
    tag_count = len(all_tags)
    print "getActiveTagsForPublisher_test: Found {} tags".format(tag_count)
    assert tag_count > 0, "No tags found!"

if __name__ == '__main__':
    getActiveTagsForPublisher_test()
