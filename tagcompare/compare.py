import os
import itertools
from multiprocessing.pool import ThreadPool

import settings
import placelocal
import logger
import output
import image


LOGGER = logger.Logger("compare", writefile=True).get()
NUM_COMPARE_PROCESSES = 8


class CompareResult:
    def __init__(self):
        self.result = {
            settings.ImageErrorLevel.INVALID: 0,
            settings.ImageErrorLevel.NONE: 0,
            settings.ImageErrorLevel.SLIGHT: 0,
            settings.ImageErrorLevel.MODERATE: 0,
            settings.ImageErrorLevel.SEVERE: 0,
        }

        self.total = 0

    def __str__(self):
        return "CompareResult (total={}): \n {}".format(self.total, self.result)

    def increment(self, key):
        if key not in self.result:
            raise ValueError("Invalid key for results: %s", key)

        self.result[key] += 1
        self.total += 1
        return self.result


def __write_result_image(pathbuilder, result_image,
                         outputdir=None, info=None, prefix="merged"):
    if not outputdir:
        outputdir = pathbuilder.create(allow_partial=True)
    elif not os.path.exists(outputdir):
        os.makedirs(outputdir)

    filename = os.path.join(outputdir,
                            prefix + pathbuilder.tagname + ".png")
    LOGGER.debug("Saving merged image for %s to %s", pathbuilder.cid, filename)
    if info:
        result_image = image.add_info(result_image, info)
    result_image.save(open(filename, 'wb'))


def _merge_images(pathbuilder, configs):
    merged_image = None
    compare_pb = pathbuilder.clone(build=output.DEFAULT_BUILD_NAME)
    for c in configs:
        pb = compare_pb.clone(config=c)
        tagimage = image.normalize_img(pb.tagimage)
        image.add_label(image=tagimage, label=c)
        if not merged_image:
            merged_image = tagimage
        else:
            merged_image = image.merge_images(merged_image, tagimage)
    return merged_image


def _compare_configs(pathbuilder, configs, comparison, result):
    diff = _compare_configs_internal(pathbuilder=pathbuilder, configs=configs)
    if diff == settings.ImageErrorLevel.INVALID:
        result.increment(key=diff)
        return False

    result_image = _merge_images(pathbuilder=pathbuilder, configs=configs)
    prefix_label = comparison + "_"
    r = __handle_output(pathbuilder=pathbuilder, result_image=result_image,
                        diff=diff, prefix=prefix_label)
    result.increment(key=r)


def _compare_configs_internal(pathbuilder, configs):
    """
    Compares a given tag for all combinations of the specified list of configs
    :param pathbuilder: the pathbuilder pointing to the tag to compare
    :param configs: the list of configs to compare
    :return: the average diff from image comparison
    """
    total_diff = 0
    compare_pb = pathbuilder.clone(build=output.DEFAULT_BUILD_NAME)
    combo_count = 0
    for a, b in itertools.combinations(configs, 2):
        pba = compare_pb.clone(config=a)
        pbb = compare_pb.clone(config=b)
        pba_image = pba.tagimage
        pbb_image = pbb.tagimage
        if not os.path.exists(pba_image):
            LOGGER.error("File not found: %s", pba_image)
            return settings.ImageErrorLevel.INVALID
        if not os.path.exists(pbb_image):
            LOGGER.error("File not found: %s", pbb_image)
            return settings.ImageErrorLevel.INVALID
        total_diff += image.compare(pba.tagimage, pbb.tagimage)
        combo_count += 1
    return total_diff / combo_count


def compare(pb, cids=None, sizes=settings.DEFAULT.tagsizes,
            types=settings.DEFAULT.tagtypes,
            comparison="latest",    # TODO: Don't hardcode
            configs=None):
    if not cids:
        cids = placelocal.get_cids(cids=settings.DEFAULT.campaigns,
                                   pids=settings.DEFAULT.publishers)
    if not configs:
        configs = settings.DEFAULT.all_comparisons[comparison]

    pool = ThreadPool(processes=NUM_COMPARE_PROCESSES)
    compare_threads = []
    result = CompareResult()
    LOGGER.info("Starting compare for %s campaigns over %s configs...",
                len(cids), len(configs))

    for cid in cids:
        for s in sizes:
            for t in types:
                newpb = pb.clone(cid=cid, tagsize=s, tagtype=t)
                compare_threads.append(pool.apply_async(func=_compare_configs,
                                                        args=(newpb, configs,
                                                              comparison, result)))
    for ct in compare_threads:
        ct.get()
    LOGGER.info("Compare over configs=%s, result=%s", configs, result)
    return result


def __handle_output(pathbuilder, result_image, diff, prefix=""):
    info = {"name": pathbuilder.tagname, "diff": diff}
    result = settings.ImageErrorLevel.NONE

    if diff > settings.ImageErrorLevel.SEVERE:
        prefix += "severe_"
        result = settings.ImageErrorLevel.SEVERE
    elif diff > settings.ImageErrorLevel.MODERATE:
        prefix += "moderate_"
        result = settings.ImageErrorLevel.MODERATE
    elif diff > settings.ImageErrorLevel.SLIGHT:
        prefix += "slight_"
        result = settings.ImageErrorLevel.SLIGHT
    __write_result_image(pathbuilder=pathbuilder, result_image=result_image,
                         info=info, prefix=prefix)
    return result


def main(build=None):
    output.aggregate()

    if not build:
        build = output.generate_build_string()
    jobname = "compare_" + build
    pb = output.create(build=jobname)
    compare(pb)
    return pb


if __name__ == '__main__':
    main()
