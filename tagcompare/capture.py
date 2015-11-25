import traceback

import placelocal
import webdriver
import output
import settings


def __capture_tags_remote(capabilities, tags, pathbuilder):
    """Captures screenshots for tags with remote webdriver
    """

    # Extra params to identify the build / job
    capabilities['build'] = pathbuilder.build
    capabilities['name'] = pathbuilder.config

    print "Starting browser with capabilities: {}...".format(capabilities)
    driver = webdriver.setup_webdriver(remote=True, capabilities=capabilities)

    try:
        _capture_tags(driver, tags, pathbuilder)
    # Catching generics here because we don't want to leak a browser
    except Exception as e:
        print "Exception caught while running display_tags: {}\n{}".format(e, traceback.format_exc())
    finally:
        # Make sure to always close the browser
        driver.quit()


def capture_tags_for_all_configs(cids, pathbuilder):
    all_tags = placelocal.get_tags_for_campaigns(cids=cids)
    if not all_tags:
        print "No tags found to capture!"
        return

    print "Capturing {} tags for {} campaigns".format(len(all_tags), len(cids))

    # Use remote browsers
    all_configs = settings.DEFAULT.configs
    config_names = settings.DEFAULT.configs_in_comparison()
    for config in config_names:
        config_data = all_configs[config]
        if not config_data['enabled']:
            continue

        capabilities = config_data['capabilities']
        pathbuilder.config = config
        __capture_tags_remote(capabilities, all_tags, pathbuilder)


def _write_html(tag_html, output_path):
    if not output_path.endswith('.html'):
        output_path += ".html"

    with open(output_path, 'w') as f:
        f.write(tag_html)


def _capture_tags(driver, tags, pathbuilder):
    for cid in tags:
        tags_per_campaign = tags[cid]
        # print "debug: " + str(tags_per_campaign)
        sizes = settings.DEFAULT.tagsizes
        for tag_size in sizes:
            tag_html = tags_per_campaign[tag_size]
            webdriver._display_tag(driver, tag_html)

            # Getting ready to write to files
            pathbuilder.size = tag_size
            pathbuilder.create()

            # TODO: Only works for iframe tags atm
            tag_element = driver.find_element_by_tag_name('iframe')
            webdriver.screenshot_element(driver, tag_element, pathbuilder.tagimage)
            _write_html(tag_html=tag_html, output_path=pathbuilder.taghtml)


def main(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers):
    build = output.generate_build_string()
    pathbuilder = output.PathBuilder(build=build)
    cids = placelocal.get_cids(cids=cids, pids=pids)
    capture_tags_for_all_configs(cids=cids, pathbuilder=pathbuilder)


if __name__ == '__main__':
    main(cids=settings.DEFAULT.campaigns, pids=settings.DEFAULT.publishers)
