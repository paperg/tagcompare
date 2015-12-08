import pytest

from tagcompare import capture
from tagcompare import settings
from tagcompare import output

SETTINGS = settings.Settings(configfile='test/test_settings.json',
                             comparefile='test/test_compare.json')


@pytest.mark.integration
def test_capture_configs():
    """
    def __capture_tags_for_configs(cids, pathbuilder, configs=settings.DEFAULT.configs,
                                   comparisons=settings.DEFAULT.comparisons):
    :return:
    """
    cids = [477944]
    configs = SETTINGS.configs
    comparisons = {
        "test": ["chrome", "firefox"]
    }
    adsizes = ["medium_rectangle"]
    adtypes = ["iframe"]

    pb = output.PathBuilder(build="capture_test")
    errors = capture.__capture_tags_for_configs(cids=cids, pathbuilder=pb,
                                                configs=configs, comparisons=comparisons,
                                                tagsizes=adsizes, tagtypes=adtypes,
                                                capture_existing=True)
    assert errors, "There should be at least one error!"
    pb.rmbuild()


def __capture_tag():
    """
    def __capture_tag(pathbuilder, tags_per_campaign, capabilities,
                  capture_existing=False):
    :return:
    """
    pb = output.PathBuilder(build="capture_tag_test", config="testconfig", cid="testcid",
                            size="skyscraper", type="iframe")
    tags = {"skyscraper": {
        "iframe": "<b>iframe tag for skyscraper</b>",
        "script": "<b>script tag for skyscraper</b>",
    }}
    capabilities = {
        "platform": "Windows 7",
        "browserName": "chrome"
    }
    result = capture.__capture_tag(pathbuilder=pb, tags_per_campaign=tags,
                                   capabilities=capabilities,
                                   capture_existing=True)
    assert result, "Error capturing tags!"
