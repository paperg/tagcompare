"""We want to make a set of comparisons factoring in popular browser/OS variations
    Comparisons are determined from usage stats:
        - OS usage stats: http://www.w3schools.com/browsers/browsers_os.asp
        - Browser usage stats: http://www.w3schools.com/browsers/browsers_stats.asp

    Configs are made based on supported capabilities:
        - saucelabs: https://wiki.saucelabs.com/display/DOCS/Platform+Configurator#/
        - browserstack: https://www.browserstack.com/list-of-browsers-and-platforms?product=automate

:return:
"""

import itertools
import os

import output
import settings
import image

# TODO: is it bad to import main?
import main


# TODO: Make configurable
ERROR_THRESHOLD = 200


def compare_campaign(cid):
    pb = output.PathBuilder(cid=cid)
    compare_output(pathbuilder=pb, configs=settings.DEFAULT.configs)


def compare_configs(pathbuilder, configs):
    sizes = settings.DEFAULT.tagsizes
    result = True
    count = 0
    errcount = 0

    # Compare all combinations of configs
    for a, b in itertools.combinations(configs, 2):
        for s in sizes:
            pba = output.PathBuilder(config=a, size=s, cid=pathbuilder.cid)
            pbb = output.PathBuilder(config=b, size=s, cid=pathbuilder.cid)
            pba_img = pba.tagimage
            pbb_img = pbb.tagimage

            if not os.path.exists(pba_img):
                "Path not found for {}, skipping compare...".format(pba_img)
                result = False
                continue
            if not os.path.exists(pbb_img):
                "Path not found for {}, skipping compare...".format(pbb_img)
                result = False
                continue
            diff = image.compare(pba.tagimage, pbb.tagimage)
            count += 1
            if diff > ERROR_THRESHOLD:
                errcount += 1
                print("ERROR: {} vs {} produced diff={}".format(
                    pba.tagimage, pbb.tagimage, diff))

    print "Compared {} images, {} with errors > {}".format(count, errcount, ERROR_THRESHOLD)
    return result


def compare_output(pathbuilder, configs):
    print ""
    print "_--==== COMPARING RESULTS ====--_"
    print ""

    # TODO: Need to do n-way compare for configs - hardcoding to 2 for now
    assert pathbuilder, "No pathbuilder object!"
    assert configs, "No configs!"
    compare_configs(pathbuilder, configs)


def do_all_comparisons(cids=None, pids=None):
    cids = main.get_cids(cids=cids, pids=pids)

    for cid in cids:
        pb = output.PathBuilder(cid=cid)
        comparisons = settings.DEFAULT.comparisons
        for compname in comparisons:
            print("comparing set: {}...".format(compname))
            configs_to_compare = comparisons[compname]
            compare_configs(pathbuilder=pb, configs=configs_to_compare)


if __name__ == '__main__':
    do_all_comparisons(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
