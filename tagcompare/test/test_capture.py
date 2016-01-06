import os

import pytest

from tagcompare import capture
from tagcompare import settings
from tagcompare import output
from tagcompare import webdriver


SETTINGS = settings.Settings(configfile='test/assets/test_settings.json',
                             comparefile='test/assets/test_compare.json')


@pytest.mark.integration
def test_capture_configs():
    cids = [477944]
    configs = {
        "chrome": {
            "enabled": True,
            "capabilities": {
                "platform": "Windows 7",
                "browserName": "chrome"
            }
        },
        "chrome_beta": {
            "enabled": True,
            "capabilities": {
                "platform": "Windows 7",
                "browserName": "chrome",
                "version": "beta"
            }
        }}
    adsizes = ["medium_rectangle"]
    adtypes = ["iframe"]

    pb = output.create(build="capture_test")
    errors = capture.__capture_tags_for_configs(cids=cids, pathbuilder=pb,
                                                configs=configs,
                                                tagsizes=adsizes, tagtypes=adtypes,
                                                capture_existing=True)
    assert errors, "There should be at least one error!"
    pb.rmbuild()


@pytest.mark.integration
def test_capture_tag():
    """
    Verify that we can capture iframe and script tags
    :return:
    """
    pb = output.create(build="capture_tag_test", config="testconfig", cid="testcid",
                       tagsize="skyscraper", tagtype="iframe")
    tags = {"skyscraper": {
        "iframe": "<iframe>iframe tag for skyscraper</iframe>",
        "script": "<script>script tag for skyscraper</script>",
    }}
    capabilities = {
        "platform": "Windows 7",
        "browserName": "chrome"
    }
    driver = webdriver.setup_webdriver(capabilities)
    result = capture.__capture_tag(pathbuilder=pb, tags_per_campaign=tags,
                                   driver=driver,
                                   capture_existing=True)
    driver.quit()
    assert result is not None, "Could not capture tags!"
    assert result is not False, "Tag capture skipped!"
    assert len(result) == 0, "Errors while capturing tags!"
    assert os.path.exists(pb.tagimage), "tagimage was not captured!"
    assert os.path.exists(pb.taghtml), "taghtml was not captured!"
    pb.rmbuild()
