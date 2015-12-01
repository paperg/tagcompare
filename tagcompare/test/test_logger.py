import os

import pytest

from tagcompare import logger


def test_init():
    testlogger = logger.Logger(name="test1")
    assert testlogger.name == "test1", "Incorrect name for testlogger!"


def test_init_with_writefile():
    testlogger = logger.Logger(name="test2", writefile=True)
    __test_logger_write_file(testlogger)


def test_init_with_directory():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    testlogger = logger.Logger(name="test3", directory=current_dir,
                               writefile=True)
    __test_logger_write_file(testlogger)


def test_init_invalid_params():
    with pytest.raises(ValueError):
        testlogger = logger.Logger(name="test4", directory="invalid_test_path")
    with pytest.raises(IOError):
        testlogger = logger.Logger(name="test5", directory="invalid_test_path",
                                   writefile=True)
    with pytest.raises(ValueError):
        testlogger = logger.Logger(name="test6")
        filename = testlogger.filepath


def test_logger_name():
    testlogger = logger.Logger("test7.log")
    assert testlogger.name == "test7", \
        "We should be stripping .log from the name"
    assert testlogger.get().name == "tagcompare.test7.log", \
        "The logger object's full name is incorrect!"


def __test_logger_write_file(testlogger):
    assert testlogger.filepath, "No filepath to write files to!"
    log = testlogger.get()
    assert logger, "Could not get logger!"
    log.debug("This is a test message that should write to file")
    log.info("This is a test message that should write to file")
    log.warn("This is a test message that should write to file")
    assert os.path.exists(
        testlogger.filepath), "path doesn't exist at %s" % testlogger.filepath
    os.remove(testlogger.filepath)  # cleanup
