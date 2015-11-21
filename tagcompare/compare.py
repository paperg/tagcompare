import itertools

import output
import settings
import image


# TODO: Make configurable
ERROR_THRESHOLD = 200


def compare_campaign(cid):
    pb = output.PathBuilder(cid=cid)
    compare_output(pathbuilder=pb, configs=settings.DEFAULT.configs)


# TODO: Refactor to new module
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
            if not pba.validate():
                "Path not found for {}, skipping compare...".format(pba.path)
                result = False
                continue
            if not pbb.validate():
                "Path not found for {}, skipping compare...".format(pbb.path)
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


# TODO: Refactor to new module
def compare_output(pathbuilder, configs):
    print ""
    print "_--==== COMPARING RESULTS ====--_"
    print ""

    # TODO: Need to do n-way compare for configs - hardcoding to 2 for now
    assert pathbuilder, "No pathbuilder object!"
    assert configs, "No configs!"
    compare_configs(pathbuilder, configs)


if __name__ == '__main__':
    for cid in settings.DEFAULT.campaigns:
        compare_campaign(cid=cid)
