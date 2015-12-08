import os
import shutil

import pytest

from tagcompare import output


TESTPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))


def __assert_correct_path(pathbuilder):
    expectedstr = "{}/{}/{}/{}/{}/{}".format(
        output.OUTPUT_DIR, pathbuilder.build, pathbuilder.config,
        pathbuilder.cid, pathbuilder.size, pathbuilder.type)
    print "expected: {}".format(expectedstr)
    print "actual: {}".format(pathbuilder.path)
    assert str(pathbuilder.path).endswith(expectedstr)


def __rmbuild_and_validate(pb):
    result = pb.rmbuild()
    assert not os.path.exists(pb.path), "Path should not exist after removal!"
    return result


def __get_pathbuilder(build="testbuild", config="testconfig", cid=0, size="testsize",
                      tagtype="testtype"):
    return output.PathBuilder(config=config, cid=cid, size=size,
                              build=build, type=tagtype)


def test_pathbuilder_create():
    pathbuilder = __get_pathbuilder()
    result = pathbuilder.create()
    print "result path: {}".format(result)
    assert pathbuilder.pathexists(), "result path '{}' wasn't created!".format(result)

    # Make sure the structure is proper
    __assert_correct_path(pathbuilder)
    __rmbuild_and_validate(pathbuilder)


def test_pathbuilder_path():
    pathbuilder = __get_pathbuilder()
    __assert_correct_path(pathbuilder)

    # Test we will get the right path after changing params
    pathbuilder.cid = 9  # Check that using a int instead of str for cid is OK
    __assert_correct_path(pathbuilder)
    pathbuilder.size = "testsize1"
    __assert_correct_path(pathbuilder)


def test_aggregate():
    result = output.aggregate()
    assert result == output.DEFAULT_BUILD_PATH, "output.aggregate() was not successful!"
    assert os.path.exists(result), "Aggregate result path does not exist: %s!" % result

    with pytest.raises(ValueError):
        output.aggregate(outputdir="invalid/path")


def test_aggregate_custom():
    asset_path = os.path.join(TESTPATH, "assets")
    custom_dir = output.aggregate(outputdir=asset_path)
    assert os.path.exists(custom_dir), "Aggregate dir should exist!"
    children = os.listdir(custom_dir)
    assert len(children) == 12, "There should be stuff aggregated!"
    shutil.rmtree(custom_dir)


def test_parse_path():
    pathbuilder = __get_pathbuilder()
    pathbuilder.create()
    pathbuilder2 = output.PathBuilder(dirpath=pathbuilder.path)
    __rmbuild_and_validate(pathbuilder)
    assert pathbuilder2, "Could not initialize PathBuilder object with dirpath"
    assert pathbuilder.path == pathbuilder2.path, "The paths don't match!"
    assert pathbuilder == pathbuilder2, "PathBuilder equals did not match!"


def test_to_str():
    pathbuilder = output.PathBuilder(build="testbuild")
    assert str(pathbuilder) == "testbuild"


def test_pathbuilder_basepath():
    testpath = TESTPATH
    build = "basepath_test"
    pb = output.PathBuilder(basepath=testpath,
                            build=build)
    assert pb.path == os.path.join(testpath, build)
    assert not os.path.exists(pb.path), "path should not exist yet!"
    created_path = pb.create(allow_partial=True)
    assert os.path.exists(created_path), "failed to create path!"
    assert __rmbuild_and_validate(pb), "rmbuild should have returned true!"


def test_pathbuilder_rmbuild_invalid():
    pb = output.PathBuilder(build="invalid")
    result = __rmbuild_and_validate(pb)
    assert not result, "There should have been nothing to remove!"


def test_pathbuilder_clone():
    pb1 = output.PathBuilder(build="clonebuild", config="cloneconfig", cid="clonecid",
                             size="clonesize", type="clonetype")
    pb2 = pb1.clone()
    assert pb1.path == pb2.path, "Clones should equal each other in path!"
    assert str(pb1) == str(pb2), "Clones should equal each other in str()!"
    pb3 = pb1.clone(build="clonebuild2")
    assert pb1.build != pb3.build, \
        "Cloned build should have been overwritten to clonebuild2!"
    assert pb1.type == pb3.type, "Clones should have the same type!"

    basepath = os.path.join(TESTPATH, "clonebase")
    pb4 = pb1.clone(basepath=basepath)
    assert basepath in str(pb4.path), "basepath should be part of the cloned path!"
    pb5 = pb4.clone()
    assert basepath in str(pb5.path), "basepath should be part of the cloned path!"
