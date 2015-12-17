from multiprocessing.pool import ThreadPool
import os

import selenium

import placelocal
import webdriver
import output
import settings
import logger


LOGGER = logger.Logger(name="capture", writefile=True).get()


def __capture_tags_for_configs(cids, pathbuilder,
                               comparisons=settings.DEFAULT.comparisons,
                               configs=settings.DEFAULT.configs,
                               tagsizes=settings.DEFAULT.tagsizes,
                               tagtypes=settings.DEFAULT.tagtypes,
                               capture_existing=False):
    all_tags = placelocal.get_tags_for_campaigns(cids=cids)
    if not all_tags:
        LOGGER.warn("No tags found to capture!")
        return

    LOGGER.info("Capturing tags for %s campaigns", len(cids))
    errors = []
    all_configs = configs
    config_names = settings.get_unique_configs_from_comparisons(comparisons)
    pool = ThreadPool(processes=10)
    results = {}

    for config_name in config_names:
        config_data = all_configs[config_name]
        if not config_data['enabled']:
            LOGGER.debug("Skipping disabled config %s" % config_name)
            continue

        pathbuilder.config = config_name
        capabilities = config_data['capabilities']
        capabilities['name'] = config_name
        capabilities['build'] = "tagcompare_" + pathbuilder.build
        capabilities['maxDuration'] = 3 * 60 * 60  # 3h max duration

        cpb = pathbuilder.clone()
        results[config_name] = pool.apply_async(func=__capture_tags,
                                                args=(capabilities, all_tags, cpb,
                                                      tagsizes, tagtypes,
                                                      capture_existing))
    for config_name in results:
        errors += results[config_name].get()
    if errors:
        LOGGER.error("%s found console errors:\n%s", pathbuilder.build, errors)
    return errors


def __write_html(tag_html, output_path):
    if not output_path.endswith('.html'):
        output_path += ".html"

    if os.path.exists(output_path):
        return

    LOGGER.debug("Writing html tag to file at %s", output_path)
    with open(output_path, 'w') as f:
        f.write(tag_html)

def __capture_preview(pathbuilder, driver,  capture_existing=False):
    """
    Captures a preview
    :param pathbuilder:
    :param driver:
    :param capture_existing:
        False on error, None on skip
    """
    # Check if we already have the files from default path
    default_pb = pathbuilder.clone(build=output.DEFAULT_BUILD_NAME)
    if default_pb.pathexists() and not capture_existing:
        LOGGER.debug("Skipping existing captures %s", default_pb.path)
        return None

    try:
        webdriver.display_preview(driver, pathbuilder)
        # Getting ready to write to files
        pathbuilder.create()
        tag_element = driver.find_element_by_css_selector("div[style]")
        webdriver.screenshot_element(driver, tag_element, pathbuilder.tagimage)
    except selenium.common.exceptions.WebDriverException:
        LOGGER.exception("Exception while capturing tags!")
        return False

    return []


def __capture_tag(pathbuilder, tags_per_campaign, driver,
                  capture_existing=False):
    """
    Captures a tag
    :param pathbuilder:
    :param tags_per_campaign:
    :param tagsize:
    :param capabilities:
    :param capture_existing:
    :return: list of browser errors during capture.
        False on error, None on skip
    """
    # Check if we already have the files from default path
    default_pb = pathbuilder.clone(build=output.DEFAULT_BUILD_NAME)
    if default_pb.pathexists() and not capture_existing:
        LOGGER.debug("Skipping existing captures %s", default_pb.path)
        return None

    try:
        tag_html = tags_per_campaign[pathbuilder.tagsize][pathbuilder.tagtype]
        errors = webdriver.display_tag(driver, tag_html)
        # Getting ready to write to files
        pathbuilder.create()
        tag_element = driver.find_element_by_tag_name(pathbuilder.tagtype)
        webdriver.screenshot_element(driver, tag_element, pathbuilder.tagimage)
    except selenium.common.exceptions.WebDriverException:
        LOGGER.exception("Exception while capturing tags!")
        return False

    __write_html(tag_html=tag_html, output_path=pathbuilder.taghtml)
    return errors


def __capture_tags(capabilities, tags, pathbuilder,
                   tagsizes=settings.DEFAULT.tagsizes,
                   tagtypes=settings.DEFAULT.tagtypes,
                   capture_existing=False):
    num_existing_skipped = 0
    num_captured = 0
    browser_errors = []
    driver = webdriver.setup_webdriver(capabilities)

    try:
        for cid in tags:
            pathbuilder.cid = cid
            tags_per_campaign = tags[cid]
            LOGGER.debug("tags_per_campaign: %s", str(tags_per_campaign))
            # TODO: Refactor better with __capture_tag
            # It's weird that we pass in a pathbuilder object and do two nested loops here
            for tagsize in tagsizes:
                pathbuilder.tagsize = tagsize
                for tagtype in tagtypes:
                    pathbuilder.tagtype = tagtype
                    if "preview" in tagtype:
                        r = __capture_preview(pathbuilder,
                                              driver,
                                              capture_existing)
                    else:
                        r = __capture_tag(pathbuilder=pathbuilder,
                                          tags_per_campaign=tags_per_campaign,
                                          driver=driver,
                                          capture_existing=capture_existing)
                    if r is None:
                        num_existing_skipped += 1
                    elif r is False:
                        continue
                    else:
                        browser_errors += r
                        num_captured += 1
    except KeyboardInterrupt:
        driver.quit()
        driver = None
    finally:
        if driver:
            driver.quit()
    LOGGER.info(
        "Captured %s tags, skipped %s existing tags for config=%s.  Found %s errors",
        num_captured, num_existing_skipped, capabilities, len(browser_errors))
    return browser_errors


def main(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers):
    """
    Runs capture, returns the job name for the capture job
    :param cids:
    :param pids:
    :return:
    """
    original_build = output.generate_build_string()
    build = "capture_" + original_build
    pathbuilder = output.create(build=build)
    cids = placelocal.get_cids(cids=cids, pids=pids)
    output.aggregate()
    __capture_tags_for_configs(cids=cids, pathbuilder=pathbuilder)
    return original_build


if __name__ == '__main__':
    main(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
