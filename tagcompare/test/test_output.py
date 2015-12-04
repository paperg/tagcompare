from tagcompare import output


def __assert_correct_path(pathbuilder):
    expectedstr = "output/{}/{}/{}/{}".format(
        pathbuilder.build, pathbuilder.config, pathbuilder.cid, pathbuilder.size)
    print "expected: {}".format(expectedstr)
    print "actual: {}".format(pathbuilder.path)
    assert str(pathbuilder.path).endswith(expectedstr)


def test_pathbuilder_create():
    pathbuilder = output.PathBuilder(config="testconfig", cid=0, size="testsize",
                                     build="testbuild")
    result = pathbuilder.create()
    print "result path: {}".format(result)
    assert pathbuilder.pathexists(), "result path '{}' wasn't created!".format(result)

    # Make sure the structure is proper
    __assert_correct_path(pathbuilder)
    pathbuilder.rmbuild()
    assert not pathbuilder.pathexists(),\
        "Failed to clean up after creating path at %s" % pathbuilder.path


def test_pathbuilder_path():
    pathbuilder = output.PathBuilder(config="testconfig", cid=0, size="testsize",
                                     build="testbuild")
    __assert_correct_path(pathbuilder)

    # Test we will get the right path after changing params
    pathbuilder.cid = 9  # Check that using a int instead of str for cid is OK
    __assert_correct_path(pathbuilder)
    pathbuilder.size = "testsize1"
    __assert_correct_path(pathbuilder)


def test_aggregate():
    result = output.aggregate()
    assert result, "output.aggregate() was not successful!"


def test_parse_path():
    pathbuilder = output.PathBuilder(config="testconfig", cid=0, size="testsize",
                                     build="testbuild")
    pathbuilder.create()
    pathbuilder2 = output.PathBuilder(dirpath=pathbuilder.path)
    pathbuilder.rmbuild()
    assert pathbuilder2, "Could not initialize PathBuilder object with dirpath"
    assert pathbuilder.path == pathbuilder2.path, "The paths don't match!"
    assert pathbuilder == pathbuilder2, "PathBuilder equals did not match!"


def test_to_str():
    pathbuilder = output.PathBuilder(build="testbuild")
    assert str(pathbuilder) == "testbuild"
