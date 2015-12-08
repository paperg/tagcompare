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
    testpath = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'assets')

    # Make sure we aggregate before a compare
    # TODO: This test is more like an integration test in that it tests aggregation
    aggregate_path = output.aggregate(outputdir=testpath)
    assert aggregate_path == os.path.join(testpath, output.DEFAULT_BUILD_NAME)
    assert os.path.exists(aggregate_path), "aggregate path doesn't exist!"
    assert len(os.listdir(aggregate_path)) == 12, \
        "there should be exactly 12 configs aggregated!"

    build = "testbuild"
    cid = 477944
    pb = output.PathBuilder(basepath=testpath,
                            build=build, cid=cid)
    build_path_expected = os.path.join(testpath, build)
    assert pb.path == build_path_expected, "Incorrect build path!"
    __test_compare_configs(pb, configs=["chrome", "chrome_beta"],
                           expected_errors=0, expected_total=4, expected_skips=0)
    __test_compare_configs(pb, configs=["chrome", "firefox"],
                           expected_errors=3, expected_total=4, expected_skips=0)
    shutil.rmtree(aggregate_path)


def __test_compare_configs(pb, configs, expected_errors, expected_total, expected_skips):
    errors, total, skips = compare.compare_configs(
        pathbuilder=pb, configs=configs)

    assert errors == expected_errors, \
        "Compare test configs: %s - Should be 0 errors!" % configs
    assert total == expected_total, \
        "Compare test configs: %s - Should be 4 compares!" % configs
    assert skips == expected_skips, \
        "Compare test configs: %s - Should be 0 skips!" % configs
