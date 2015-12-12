import os
import shutil

from tagcompare import compare
from tagcompare import output
from tagcompare import settings


settings.TEST_MODE = True


def test_compare_configs():
    """
    def compare_configs(pathbuilder, configs):
    :return:
    """
    testpath = settings.Test.TEST_ASSETS_DIR
    expected_aggregate_path = os.path.join(testpath, output.DEFAULT_BUILD_NAME)

    # Make sure we aggregate before a compare
    # TODO: This test is more like an integration test in that it tests aggregation
    assert not os.path.exists(
        expected_aggregate_path), "aggregate path already exists!"
    aggregate_path = output.aggregate(outputdir=testpath)
    assert aggregate_path == expected_aggregate_path, \
        "aggregate path is not as expected!"
    assert os.path.exists(aggregate_path), "aggregate path doesn't exist!"

    build = "testbuild"
    cid = 477944
    pb = output.create(basepath=testpath,
                       build=build, cid=cid)
    __test_compare_configs(pb, configs=["chrome", "chrome_beta"],
                           expected_errors=0, expected_total=4,
                           expected_skips=0)
    __test_compare_configs(pb, configs=["chrome", "firefox"],
                           expected_errors=3, expected_total=4,
                           expected_skips=0)
    shutil.rmtree(aggregate_path)


def __test_compare_configs(pb, configs, expected_errors, expected_total,
                           expected_skips):
    errors, total, skips = compare.compare_configs(
        pathbuilder=pb, configs=configs)

    assert errors == expected_errors, \
        "Compare test configs: %s - Should be 0 errors!" % configs
    assert total == expected_total, \
        "Compare test configs: %s - Should be 4 compares!" % configs
    assert skips == expected_skips, \
        "Compare test configs: %s - Should be 0 skips!" % configs
