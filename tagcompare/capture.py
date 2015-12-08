import selenium

import placelocal
import webdriver
import output
import settings
import logger


LOGGER = logger.Logger(name=__name__, writefile=True).get()


def __capture_tags_for_configs(cids, pathbuilder,
                               comparisons=settings.DEFAULT.comparisons,
                               configs=settings.DEFAULT.configs,
                               tagsizes=settings.DEFAULT.tagsizes,
                               tagtypes=settings.DEFAULT.tagtypes,
                               capture_existing=False):
    all_tags, num_tags = placelocal.get_tags_for_campaigns(cids=cids)
    if not all_tags:
        LOGGER.warn("No tags found to capture!")
        return

    LOGGER.info(
        "Found %s tags for %s campaigns", num_tags, len(cids))

    errors = []
    all_configs = configs
    config_names = settings.get_unique_configs_from_comparisons(comparisons)
    for config in config_names:
        config_data = all_configs[config]
        if not config_data['enabled']:
            LOGGER.debug("Skipping disabled config %s" % config)
            continue

        pathbuilder.config = config
        capabilities = config_data['capabilities']
        capabilities['name'] = str(pathbuilder)
        capabilities['build'] = pathbuilder.build
        errors += __capture_tags(capabilities, all_tags, pathbuilder,
                                 capture_existing=capture_existing,
                                 tagsizes=tagsizes, tagtypes=tagtypes)
    LOGGER.error("%s found console errors:\n%s", pathbuilder.build, errors)
    return errors


def __write_html(tag_html, output_path):
    if not output_path.endswith('.html'):
        output_path += ".html"

    with open(output_path, 'w') as f:
        f.write(tag_html)


def __capture_tag(pathbuilder, tags_per_campaign, capabilities,
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

    driver = webdriver.setup_webdriver(capabilities)
    try:
        tag_html = tags_per_campaign[pathbuilder.size][pathbuilder.type]
        errors = webdriver.display_tag(driver, tag_html)
        # Getting ready to write to files
        pathbuilder.create()
        tag_element = driver.find_element_by_tag_name(pathbuilder.type)
        webdriver.screenshot_element(driver, tag_element, pathbuilder.tagimage)
    except selenium.common.exceptions.WebDriverException:
        LOGGER.exception("Exception while capturing tags!")
        driver.quit()
        return False

    driver.quit()
    __write_html(tag_html=tag_html, output_path=pathbuilder.taghtml)
    return errors


def __capture_tags(capabilities, tags, pathbuilder,
                   tagsizes=settings.DEFAULT.tagsizes, tagtypes=settings.DEFAULT.tagtypes,
                   capture_existing=False):
    num_existing_skipped = 0
    num_captured = 0

    LOGGER.info("Capturing %s tags for config %s", len(tags), capabilities)
    browser_errors = []
    for cid in tags:
        pathbuilder.cid = cid
        tags_per_campaign = tags[cid]
        LOGGER.debug("tags_per_campaign: %s", str(tags_per_campaign))
        # TODO: Refactor better with __capture_tag
        # It's weird that we pass in a pathbuilder object and do two nested loops here
        for tagsize in tagsizes:
            pathbuilder.size = tagsize
            for tagtype in tagtypes:
                pathbuilder.type = tagtype
                r = __capture_tag(pathbuilder=pathbuilder,
                                  tags_per_campaign=tags_per_campaign,
                                  capabilities=capabilities,
                                  capture_existing=capture_existing)
                if r is None:
                    num_existing_skipped += 1
                elif r is False:
                    continue
                else:
                    browser_errors += r
                    num_captured += 1

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
    build = output.generate_build_string()
    pathbuilder = output.PathBuilder(build=build)
    cids = placelocal.get_cids(cids=cids, pids=pids)
    output.aggregate()
    __capture_tags_for_configs(cids=cids, pathbuilder=pathbuilder)
    return pathbuilder.build


if __name__ == '__main__':
    main(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
