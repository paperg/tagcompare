"""Handles output files from the tagcompare tool
    - Creates output directories before a run
    - Compares the test configs with the result/output configs
    - Utility methods for getting the right path to outputs
"""
import os
import time
import glob
from distutils import dir_util

import logger


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DEFAULT_BUILD_NAME = "default"
DEFAULT_BUILD_PATH = os.path.join(OUTPUT_DIR, DEFAULT_BUILD_NAME)

COMPARE_NAME = "compare"
COMPARE_PATH = os.path.join(OUTPUT_DIR, COMPARE_NAME)

LOGGER = logger.Logger(name=__name__, writefile=False).get()


class PathBuilder():
    """Class to store & build paths/partial paths to outputs of tagcompare
    """
    # TODO: Consider making this class immutable
    def __init__(self, build=None, config=None, cid=None, size=None,
                 dirpath=None):
        if dirpath:
            self.__parse(dirpath)
        else:
            self.config = config
            self.cid = cid
            self.size = size
            self.__build = build
            if not self.__build:
                raise ValueError('build must be set!')

    def __eq__(self, other):
        if not isinstance(other, PathBuilder):
            return False
        return self.path == other.path

    def __str__(self):
        # TODO: Handle cases where not all values are initialized
        return self.path


    def __parse(self, dirpath):
        """
        Given a 'dirpath' which corresponds to a path produced by PathBuilder, make the PathBuilder object
        :param dirpath: should be a real path ending in 'output/{build}/{config}/{cid}/{size}/'
        """
        if not dirpath or not isinstance(dirpath, basestring):
            raise ValueError(
                'path is not defined or not a string.  path: {}'.format(
                    dirpath))
        if not os.path.exists(dirpath):
            raise ValueError('path does not exist!  path: {}'.format(dirpath))

        allparts = []
        # Split 4 parts for build, config, cid, size
        # TODO: error checks
        tmp_path = dirpath
        for i in range(0, 4):
            parts = os.path.split(tmp_path)
            assert len(
                parts) == 2, \
                "Not enough parts to the path! parts={}, dirpath={}".format(
                parts, dirpath)
            tmp_path = parts[0]
            allparts.insert(0, parts[1])

        self.__build = allparts[0]
        self.config = allparts[1]
        self.cid = str(allparts[2])
        self.size = allparts[3]

    @property
    def build(self):
        """
        Read-only property - can only be set on init or internally
        :return:
        """
        return self.__build

    @property
    def path(self):
        """Gets the output path for a given config, cid and size
        Returns partial paths if optional parameters aren't provided
        """
        self.__normalize_params()
        result = os.path.join(OUTPUT_DIR, self.build)
        if not self.config:
            raise ValueError("config is not set!")
        result = os.path.join(result, self.config)
        if not self.cid:
            raise ValueError("cid is not set!")
        result = os.path.join(result, self.cid)
        if not self.size:
            raise ValueError("size is not set!")
        result = os.path.join(result, self.size)
        return result

    def clone(self, build=None, config=None, cid=None, size=None):
        """Clones the object with default values from self.  Can override specifics
        """
        if not build:
            build = self.build
        if not config:
            config = self.config
        if not cid:
            cid = self.cid
        if not size:
            size = self.size
        clone = PathBuilder(build=build, config=config, cid=cid, size=size)
        return clone

    def pathexists(self):
        return os.path.exists(self.path)

    def create(self):
        result = self.path
        if not self.pathexists():
            os.makedirs(result)
        return result

    @property
    def tagname(self):
        result = str.format("{}-{}-{}", self.cid, self.size, self.config)
        return result

    @property
    def tagimage(self):
        result = os.path.join(self.path, self.tagname + ".png")
        return result

    @property
    def taghtml(self):
        result = os.path.join(self.path, self.tagname + ".html")
        return result

    @property
    def buildpath(self):
        result = os.path.join(OUTPUT_DIR, self.build)
        return result

    def __normalize_params(self):
        if self.cid is not None:
            self.cid = str(self.cid)
        if self.config is not None:
            self.config = str(self.config)
        if self.__build is not None:
            self.__build = str(self.__build)
        if self.size is not None:
            self.size = str(self.size)


"""
Static helper methods:
"""


def aggregate():
    """
    Aggregates the captures from various campaigns to the 'default'
    :return:
    """
    buildpaths = glob.glob('output/tagcompare*/')
    LOGGER.info("Aggregating build data to %s", DEFAULT_BUILD_PATH)
    for buildpath in buildpaths:
        if str(buildpath).endswith(DEFAULT_BUILD_NAME + "/"):
            # Don't do this for the default build
            continue

        abs_buildpath = os.path.join(BASE_DIR, buildpath)
        LOGGER.debug("Copying from %s to %s", abs_buildpath, DEFAULT_BUILD_PATH)
        dir_util.copy_tree(abs_buildpath, DEFAULT_BUILD_PATH, update=1)
    return True


def generate_build_string():
    build = str.format("{}_{}", "tagcompare", time.strftime("%Y%m%d-%H%M%S"))
    return build


if __name__ == '__main__':
    aggregate()
