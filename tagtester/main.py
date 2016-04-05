#!/usr/bin/env python

import logging
import os
import argparse
import time
from contextlib import closing

from tagcompare import placelocal
from tagcompare import output
from tagcompare import settings
from tagcompare import capture
from tagcompare import image


MODULE_NAME = 'tagtester'
OUTPUT_BASEDIR = os.path.join(settings.HOME_DIR, MODULE_NAME)

# TODO: the settings dictionary should be split out to be made into test files
SETTINGS = {
    'domain': 'www.placelocalqa.com',
    'cids': [148487, 148485, 147966, 147878, 147871, 147870, 147869, 147868,
             147867, 147866, 147865, 147862],
    'sizes': ['medium_rectangle', 'skyscraper', 'halfpage'],
    'types': ['iframe'],
    'configs': ['chrome'],
    'preview': 1,
    'resubmit': False
}

LOGGER = logging.getLogger('tagtester')


def __submit_campaigns(placelocal_api, cids, wait_time=60):
    for cid in cids:
        LOGGER.info('Re-submitting campaign %s...', cid)
        placelocal_api.submit_campaign(cid)

    # It takes a minute or two after submit for it to take effect
    if wait_time > 0:
        LOGGER.info('Waiting %s after submits...', wait_time)
        time.sleep(wait_time)


def capture_tags():
    LOGGER.info(
        'Starting tagtester capture with settings: {}'.format(SETTINGS))
    test_domain = SETTINGS['domain']
    test_cids = SETTINGS['cids']
    test_sizes = SETTINGS['sizes']
    test_types = SETTINGS['types']
    test_configs = SETTINGS['configs']
    preview = SETTINGS['preview']
    resubmit = SETTINGS['resubmit']

    placelocal_api = placelocal.PlaceLocalApi(domain=test_domain)

    build = output.generate_build_string(prefix='tagtester')
    pb = output.create(build, basepath=OUTPUT_BASEDIR)
    placelocal_api = placelocal.PlaceLocalApi(domain=test_domain)

    if resubmit:
        __submit_campaigns(placelocal_api, cids=test_cids)

    browser_errors = {}
    tag_count = 0
    for config in test_configs:
        tags = placelocal_api.get_tags_for_campaigns(
            cids=test_cids, ispreview=preview)
        with closing(capture.TagCapture.from_config(config)) as tagcapture:
            for cid in test_cids:
                for s in test_sizes:
                    for t in test_types:
                        tag_count += 1
                        pb.cid = cid
                        pb.tagsize = s
                        pb.tagtype = t
                        pb.config = config
                        taghtml = tags[cid][s][t]
                        pb.create()
                        try:
                            browser_errors[pb.tagname] = tagcapture.capture_tag(
                                tag_html=taghtml,
                                output_path=pb.tagimage, tagtype=t)
                        except Exception as ex:
                            LOGGER.warn('Caught exception:\n%s', ex)
                            continue
                        LOGGER.info('Captured {}'.format(pb.tagimage))

    if browser_errors:
        LOGGER.error('Found browser errors in {} tags:\n{}'.format(
            len(browser_errors), browser_errors))
    else:
        LOGGER.info('Completed capture of {} tags'.format(tag_count))
    return build


def compare_builds(build, reference='golden'):
    """
    Compares a build against a reference build, (by default named 'golden' build)
    :param buildname:
    :param golden:
    :return:
    """
    compare_build = build + "_vs_" + reference
    LOGGER.info('Starting compare build: %s', compare_build)

    # Compare all the tag images in the build path against the golden set
    build_paths = output.get_all_paths(buildname=build, basedir=OUTPUT_BASEDIR)
    compare_errors = {}

    for bp in build_paths:
        build_pb = output.create_from_path(bp, basepath=OUTPUT_BASEDIR)
        ref_pb = build_pb.clone(build=reference)

        # We can compare iff both paths exists
        build_image = build_pb.tagimage
        ref_image = ref_pb.tagimage
        if not os.path.exists(build_image):
            LOGGER.warn('SKIPPING compare: path does not exist at {}'.format(
                build_pb.path))
            continue
        if not os.path.exists(ref_image):
            LOGGER.warn('SKIPPING compare: path does not exist at {}'.format(
                ref_pb.path))
            # TODO: In this case we want to have the option of making new ref
            continue

        result = image.compare(build_pb.tagimage, ref_pb.tagimage)
        LOGGER.debug('Result for %s: %s', compare_build, result)
        if result > settings.ImageErrorLevel.SLIGHT:
            compare_errors[build_image] = result
            LOGGER.warn('Invalid compare result for %s', build_image)

    LOGGER.info('Finished compare build %s for %s images!  Found %s errors:\n%s',
                compare_build, len(build_paths), len(compare_errors), compare_errors)
    return True


def __parse_args():
    """
    Handles parsing commandline args and set appropriate settings from them
    :return: the key/value pair for the commandline args parsed
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--compare-build',
                        default=None,
                        help='Specify a build name to compare with the reference set')

    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Enable verbose logging for debugging')
    args = parser.parse_args()
    logging.debug("tagtester params: %s", args)
    return args


def main():
    args = __parse_args()
    if args.verbose:
        print('verbose logging mode!')
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)

    if not args.compare_build:
        build = capture_tags()
    else:
        build = args.compare_build

    compare_builds(build)

if __name__ == '__main__':
    main()
