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
import placelocal


def compare_campaign(cid):
    pb = output.PathBuilder(cid=cid)
    compare_configs(pathbuilder=pb, configs=settings.DEFAULT.configs)


def compare_configs(pathbuilder, configs):
    # TODO: Should we check if configs are enabled before comparing?
    assert pathbuilder, "No pathbuilder object!"
    assert configs, "No configs!"

    sizes = settings.DEFAULT.tagsizes
    count = 0
    errorcount = 0
    skipcount = 0

    # Compare all combinations of configs
    for a, b in itertools.combinations(configs, 2):
        for s in sizes:
            pba = output.PathBuilder(build=pathbuilder.build, config=a, size=s, cid=pathbuilder.cid)
            pbb = output.PathBuilder(build=pathbuilder.build, config=b, size=s, cid=pathbuilder.cid)
            pba_img = pba.tagimage
            pbb_img = pbb.tagimage
            count += 1
            compare_result = compare_images(pba_img, pbb_img, pathbuilder)
            if compare_result is None:
                skipcount += 1
            elif compare_result is False:
                errorcount += 1

    print "Compared {} images: {} errors, {} skipped".format(count, errorcount, skipcount)
    return errorcount, count, skipcount


def compare_images(file1, file2, pathbuilder):
    """Compares two image files, returns True if compare took place, False otherwise
    :param file1:
    :param file2:
    :return:
    """
    compare_name = __get_compare_name(file1, file2)
    if not os.path.exists(file1):
        print str.format("SKIPPING {} - {} not found!", compare_name, file1)
        return None
    if not os.path.exists(file2):
        print str.format("SKIPPING {} - {} not found!", compare_name, file2)
        return None

    diff = image.compare(file1, file2)
    if diff is False:
        # Unable to produce diff due to errors
        return False

    if diff > image.ERROR_THRESHOLD:
        __write_merged_image(file1, file2, diff, build=pathbuilder.build)
        return False

    return True


def __get_compare_name(file1, file2):
    filename1 = os.path.basename(file1)
    filename2 = os.path.basename(file2)
    compare_name = str.format("{}__vs__{}".format(
        os.path.splitext(filename1)[0], os.path.splitext(filename2)[0]))
    return compare_name


def __write_merged_image(file1, file2, diff, build):
    compare_name = __get_compare_name(file1, file2)

    # Generate additional info in output
    # TODO: Refactor to own function
    mergedimg = image.merge_images(file1, file2)
    info = {"name": compare_name, "diff": diff}
    mergedimg2 = image.add_info(mergedimg, info)

    compare_dir = os.path.join(output.OUTPUT_DIR, "compare")
    build_dir = os.path.join(compare_dir, build)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    merged_path = os.path.join(build_dir, compare_name + ".png")
    print "Writing merged image file at {}".format(merged_path)
    mergedimg2.save(open(merged_path, 'wb'))
    print("ERROR: {} vs {} produced diff={}".format(
        file1, file2, diff))


def do_all_comparisons(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers):
    cids = placelocal.get_cids(cids=cids, pids=pids)

    total_compares = 0
    total_errors = 0
    total_skipped = 0
    # Always compare against the default which will have all the aggregated data
    pb = output.PathBuilder(build=output.DEFAULT_BUILD_NAME)

    for cid in cids:
        pb.cid = cid
        comparisons = settings.DEFAULT.comparisons
        for name in comparisons:
            print("")
            print("*** Comparing set: {}...".format(name))
            configs_to_compare = comparisons[name]
            errors, count, skipped = compare_configs(pathbuilder=pb, configs=configs_to_compare)
            total_errors += errors
            total_compares += count
            total_skipped += skipped

    print ""
    print "*** RESULTS ***"
    print "Compared {} images: {} errors, {} skipped".format(total_compares, total_errors, total_skipped)
    print "See additional logs at: {}".format(pb.buildpath)


if __name__ == '__main__':
    do_all_comparisons(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
