import pytest
from tagcompare import compare

from tagcompare import output
from tagcompare import settings

settings.TEST_MODE = True


@pytest.mark.integration
def test_compare():
    """
    def compare(pb, cids=None, sizes=settings.DEFAULT.tagsizes,
            types=settings.DEFAULT.tagtypes,
            comparison="latest",
            configs=None):
    :return:
    """
    testpath = settings.Test.TEST_ASSETS_DIR
    build = "testcompare"
    cids = [477944]
    comparison = "latest"
    pb = output.create(build=build, basepath=testpath)
    result = compare.compare(pb=pb, cids=cids, comparison=comparison)
    assert result.result[settings.ImageErrorLevel.INVALID] == 0, \
        "There should be 0 invalid results!"
    assert len(result.result) > 0, "There should be some results!"
    pb.rmbuild()


@pytest.mark.integration
def test_compare_configs():
    """
    def compare_configs(pathbuilder, configs):
    :return:
    """
    testpath = settings.Test.TEST_ASSETS_DIR
    build = "testbuild"
    cid = 477944
    pb = output.create(basepath=testpath,
                       build=build, cid=cid,
                       tagsize="medium_rectangle", tagtype="iframe")
    __test_compare_configs_internal(pb, configs=["chrome", "chrome_beta"],
                                    expected_result=0)
    __test_compare_configs_internal(pb, configs=["chrome", "firefox"],
                                    expected_result=214)


def __test_compare_configs_internal(pb, configs, expected_result):
    result = compare._compare_configs_internal(
        pathbuilder=pb, configs=configs)
    assert result != settings.ImageErrorLevel.INVALID, "Invalid result!"
    assert result == expected_result, "Result was not expected!"
