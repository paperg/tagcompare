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
import main  # TODO: Probably not appropriate to import main


def compare_campaign(cid):
    pb = output.PathBuilder(cid=cid)
    compare_configs(pathbuilder=pb, configs=settings.DEFAULT.configs)


def compare_configs(pathbuilder, configs):
    assert pathbuilder, "No pathbuilder object!"
    assert configs, "No configs!"

    sizes = settings.DEFAULT.tagsizes
    count = 0
    errorcount = 0

    # Compare all combinations of configs
    for a, b in itertools.combinations(configs, 2):
        for s in sizes:
            pba = output.PathBuilder(config=a, size=s, cid=pathbuilder.cid)
            pbb = output.PathBuilder(config=b, size=s, cid=pathbuilder.cid)
            pba_img = pba.tagimage
            pbb_img = pbb.tagimage
            count += 1
            if not compare_images(pba_img, pbb_img, pathbuilder):
                errorcount += 1

    print "Compared {} images, {} with errors > {}".format(count, errorcount, image.ERROR_THRESHOLD)
    return errorcount, count


def compare_images(file1, file2, pathbuilder):
    """Compares two image files, returns True if compare took place, False otherwise
    :param file1:
    :param file2:
    :return:
    """
    filename1 = os.path.basename(file1)
    filename2 = os.path.basename(file2)
    compare_name = str.format("{}__vs__{}".format(
        os.path.splitext(filename1)[0], os.path.splitext(filename2)[0]))
    skip_message = "SKIPPING {} (not found)...".format(compare_name)
    if not os.path.exists(file1):
        print skip_message
        return False
    if not os.path.exists(file2):
        print skip_message
        return False

    diff = image.compare(file1, file2)
    if diff > image.ERROR_THRESHOLD:
        # Generate additional info in output
        # TODO: Refactor to own function
        mergedimg = image.merge_images(file1, file2)
        info = { "name": compare_name, "diff": diff }
        mergedimg2 = image.add_info(mergedimg, info)

        merged_dir = os.path.join(pathbuilder.buildpath, "meta")
        if not os.path.exists(merged_dir):
            os.makedirs(merged_dir)
        merged_path = os.path.join(merged_dir, compare_name + ".png")
        if not os.path.exists(merged_path):
            mergedimg2.save(open(merged_path, 'wb'))
        print("ERROR: {} vs {} produced diff={}".format(
            file1, file2, diff))
        return False

    return True


def do_all_comparisons(cids=None, pids=None):
    cids = main.get_cids(cids=cids, pids=pids)

    total_compares = 0
    total_errors = 0
    build = output.generate_build_string()
    pb = output.PathBuilder(build=build)

    for cid in cids:
        pb.cid = cid
        comparisons = settings.DEFAULT.comparisons
        for compname in comparisons:
            print("")
            print("*** Comparing set: {}...".format(compname))
            configs_to_compare = comparisons[compname]
            errors, count = compare_configs(pathbuilder=pb, configs=configs_to_compare)
            total_errors += errors
            total_compares += count

    print ""
    print "*** RESULTS ***"
    print "Compared {} images, found {} errors".format(total_compares, total_errors)
    print "See additional logs at: {}".format(pb.buildpath)


if __name__ == '__main__':
    do_all_comparisons(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
