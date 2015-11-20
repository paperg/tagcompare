import os

from tagcompare import output


def test_pathbuilder_create():
    pathbuilder = output.PathBuilder(config="test", cid=0, size="test")

    result = pathbuilder.create()
    print "result path: {}".format(result)
    assert os.path.exists(result), "result path '{}' wasn't created!".format(result)

    # Make sure the structure is proper
    configpath = os.path.join(output.OUTPUT_DIR, pathbuilder.config)
    assert os.path.exists(configpath), "config path '{}' wasn't created!".format(configpath)
    cidpath = os.path.join(configpath, str(pathbuilder.cid))
    assert os.path.exists(cidpath), "cid path '{}' wasn't created!".format(cidpath)
    sizepath = os.path.join(cidpath, pathbuilder.size)
    assert os.path.exists(sizepath), "size path '{}' wasn't created!".format(sizepath)


def test_pathbuilder_validate():
    pathbuilder = output.PathBuilder(config="test", cid=0, size="test")
    pathbuilder.create()
    assert pathbuilder.validate()


def test_pathbuilder_path():
    pathbuilder = output.PathBuilder(config="test", cid=0, size="test")
    assert str(pathbuilder.path).endswith("output/test/0/test")

    # Test we will get the right path after changing params
    pathbuilder.cid = 9
    assert str(pathbuilder.path).endswith("output/test/9/test")
    pathbuilder.size = "test1"
    assert str(pathbuilder.path).endswith("output/test/9/test1")
