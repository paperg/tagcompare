import pytest

from tagcompare import capture
from tagcompare import settings
from tagcompare import output


@pytest.mark.integration
def test_capture_configs():
    """
    def __capture_tags_for_configs(cids, pathbuilder, configs=settings.DEFAULT.configs,
                                   comparisons=settings.DEFAULT.comparisons):
    :return:
    """
    cids = [477944]
    configs = settings.DEFAULT.configs
    comparisons = {
        "test": ["chrome", "firefox"]
    }
    sizes = ["medium_rectangle"]

    pb = output.PathBuilder(build="capture_test")
    errors = capture.__capture_tags_for_configs(cids=cids, pathbuilder=pb,
                                                configs=configs, comparisons=comparisons,
                                                sizes=sizes, capture_existing=True)
    assert errors, "There should be at least one error!"
    pb.rmbuild()
