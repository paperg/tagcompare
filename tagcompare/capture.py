import placelocal
import webdriver
import output
import settings
import logger

LOGGER = logger.Logger(name=__name__, writefile=True).get()


def __start_webdriver_capture(capabilities, name, build):
    # Extra params to identify the build / job
    capabilities['build'] = build
    capabilities['name'] = name
    LOGGER.debug("Starting browser with capabilities: %s...", capabilities)
    driver = webdriver.setup_webdriver(remote=True, capabilities=capabilities)
    return driver


def capture_tags_for_all_configs(cids, pathbuilder):
    all_tags, num_tags = placelocal.get_tags_for_campaigns(cids=cids)
    if not all_tags:
        LOGGER.warn("No tags found to capture!")
        return

    LOGGER.info(
        "Capturing {} tags for {} campaigns".format(num_tags, len(cids)))

    # Use remote browsers
    all_configs = settings.DEFAULT.configs
    config_names = settings.DEFAULT.configs_in_comparison()
    for config in config_names:
        config_data = all_configs[config]
        if not config_data['enabled']:
            LOGGER.debug("Skipping disabled config %s" % config)
            continue

        capabilities = config_data['capabilities']
        pathbuilder.config = config
        __capture_tags(capabilities, all_tags, pathbuilder,
                       capture_existing=False)


def _write_html(tag_html, output_path):
    if not output_path.endswith('.html'):
        output_path += ".html"

    with open(output_path, 'w') as f:
        f.write(tag_html)


def __capture_tags(capabilities, tags, pathbuilder, capture_existing=False):
    # TODO: OMG REFACTOR BETTER
    num_existing_skipped = 0
    num_captured = 0
    for cid in tags:
        pathbuilder.cid = cid
        tags_per_campaign = tags[cid]
        LOGGER.debug("tags_per_campaign: %s", str(tags_per_campaign))
        sizes = settings.DEFAULT.tagsizes
        for tag_size in sizes:
            pathbuilder.size = tag_size

            # Check if we already have the files from default path
            default_pb = pathbuilder.clone(build=output.DEFAULT_BUILD_NAME)
            if default_pb.pathexists() and not capture_existing:
                LOGGER.debug("Skipping existing captures %s", default_pb.path)
                num_existing_skipped += 1
                continue

            try:
                driver = __start_webdriver_capture(capabilities,
                                                   build=pathbuilder.build,
                                                   name=pathbuilder.config)
                tag_html = tags_per_campaign[tag_size]
                webdriver.display_tag(driver, tag_html)
            except Exception as e:
                LOGGER.exception("Exception while displaying tags!")
                if driver:
                    driver.quit()
                continue

            # Getting ready to write to files
            pathbuilder.create()
            # TODO: Only works for iframe tags atm
            try:
                tag_element = driver.find_element_by_tag_name('iframe')
                webdriver.screenshot_element(driver, tag_element,
                                             pathbuilder.tagimage)
            except Exception as e:
                LOGGER.exception(
                    "Exception while getting screenshot for tag: %s",
                    pathbuilder.path)
                if driver:
                    driver.quit()
                continue

            if driver:
                driver.quit()

            _write_html(tag_html=tag_html, output_path=pathbuilder.taghtml)
            num_captured += 1
    LOGGER.info(
        "Captured %s tags, skipped %s existing tags for config=%s",
                num_captured, num_existing_skipped, capabilities)


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
    capture_tags_for_all_configs(cids=cids, pathbuilder=pathbuilder)
    return pathbuilder.build


if __name__ == '__main__':
    main(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
