"""Handles output files from the tagcompare tool
    - Creates output directories before a run
    - Compares the test configs with the result/output configs
    - Utility methods for getting the right path to outputs
"""
import os
import time
import glob
from distutils import dir_util
import shutil

import settings
import logger


OUTPUT_DIR = settings.OUTPUT_DIR
DEFAULT_BUILD_NAME = "default"
DEFAULT_BUILD_PATH = os.path.join(OUTPUT_DIR, DEFAULT_BUILD_NAME)
LOGGER = logger.Logger(name=__name__, writefile=False).get()


class PathBuilder():
    """Class to store & build paths/partial paths to outputs of tagcompare
    """
    # TODO: Consider making this class immutable
    def __init__(self, build=None, config=None,
                 cid=None, size=None, type=None,
                 dirpath=None, basepath=settings.OUTPUT_DIR):
        self.__basepath = basepath
        if dirpath:
            self.__parse(dirpath)
        else:
            self.config = config
            self.cid = cid
            self.size = size
            self.type = type
            self.__build = build
            if not self.__build:
                raise ValueError('build must be set!')

    def __eq__(self, other):
        if not isinstance(other, PathBuilder):
            return False
        return self.path == other.path

    def __str__(self):
        return str("{}-{}".format(
            self.build, self.tagname)) \
            .replace('None', '').rstrip('-')

    def __parse(self, dirpath):
        """
        Given a 'dirpath' which corresponds to a path produced by PathBuilder,
        make the PathBuilder object
        :param dirpath: should be a real path ending in
        '{OUTPUT_DIR}/{build}/{config}/{cid}/{size}/{type}'
        """
        if not dirpath or not isinstance(dirpath, basestring):
            raise ValueError(
                'path is not defined or not a string.  path: {}'.format(
                    dirpath))
        if not os.path.exists(dirpath):
            raise ValueError('path does not exist!  path: {}'.format(dirpath))

        allparts = []
        numparts = 5
        # Split parts for build, config, cid, size, type
        # TODO: error checks
        tmp_path = dirpath
        for i in range(0, numparts):
            parts = os.path.split(tmp_path)
            assert len(parts) == 2, \
                "Not enough parts to the path! parts={}, dirpath={}".format(
                    parts, dirpath)
            tmp_path = parts[0]
            allparts.insert(0, parts[1])

        if len(allparts) < numparts:
            raise ValueError("dirpath %s doesn't have %s parts!", dirpath, numparts)
        self.__build = allparts[0]
        self.config = allparts[1]
        self.cid = str(allparts[2])
        self.size = allparts[3]
        self.type = allparts[4]

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
        return self.__getpath(allow_partial=True)

    def clone(self, build=None, config=None,
              cid=None, size=None, type=None, basepath=None):
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
        if not type:
            type = self.type
        if not basepath:
            basepath = self.__basepath

        clone = PathBuilder(
            build=build, config=config, cid=cid, size=size, type=type, basepath=basepath)
        return clone

    def pathexists(self):
        return os.path.exists(self.path)

    def create(self, allow_partial=False):
        # Throw if one of the parameters is not set
        result = self.__getpath(allow_partial=allow_partial)
        if not os.path.exists(result):
            os.makedirs(result)
        return result

    @property
    def tagname(self):
        result = str.format("{}-{}-{}-{}",
                            self.config, self.cid, self.size, self.type)
        return result

    @property
    def tagimage(self):
        result = os.path.join(self.__getpath(allow_partial=False),
                              self.tagname + ".png")
        return result

    @property
    def taghtml(self):
        result = os.path.join(self.__getpath(allow_partial=False),
                              self.tagname + ".html")
        return result

    @property
    def buildpath(self):
        result = os.path.join(self.__basepath, self.build)
        return result

    def rmbuild(self):
        """Cleans up the files in the build path
        """
        buildpath = self.buildpath
        if os.path.exists(buildpath):
            LOGGER.debug("rmbuild for path %s", buildpath)
            shutil.rmtree(buildpath)
            return True
        return False

    def __getpath(self, allow_partial=False):
        self.__normalize_params()
        result = os.path.join(self.__basepath, self.build)
        if not self.config:
            if not allow_partial:
                raise ValueError("config is not set!")
            return result
        result = os.path.join(result, self.config)
        if not self.cid:
            if not allow_partial:
                raise ValueError("cid is not set!")
            return result
        result = os.path.join(result, self.cid)
        if not self.size:
            if not allow_partial:
                raise ValueError("size is not set!")
            return result
        result = os.path.join(result, self.size)
        if not self.type:
            if not allow_partial:
                raise ValueError("type is not set!")
            return result
        result = os.path.join(result, self.type)
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
        if self.type is not None:
            self.type = str(self.type)


"""
Static helper methods:
"""


def aggregate(outputdir=OUTPUT_DIR):
    """
    Aggregates the captures from various campaigns to the 'default'
    :return:
    """
    if not os.path.exists(outputdir):
        raise ValueError("outputdir does not exist at %s!" % outputdir)

    outputdir = str(outputdir).rstrip('/')
    buildpaths = glob.glob(outputdir + '/*/')
    aggregate_path = os.path.join(outputdir, DEFAULT_BUILD_NAME)

    if not os.path.exists(aggregate_path):
        LOGGER.debug("Creating path for aggregates at %s", aggregate_path)
        os.makedirs(aggregate_path)

    LOGGER.info("Aggregating build data to %s", aggregate_path)
    # Workaround bug with dir_util
    # See http://stackoverflow.com/questions/9160227/
    dir_util._path_created = {}
    for buildpath in buildpaths:
        if str(buildpath).endswith(DEFAULT_BUILD_NAME + "/"):
            # Don't do this for the default build
            continue

        buildpath = os.path.join(outputdir, buildpath)
        LOGGER.warn("Copying from %s to %s", buildpath,
                    aggregate_path)

        dir_util.copy_tree(buildpath, aggregate_path, update=1)
    return aggregate_path


def generate_build_string():
    build = str.format("{}_{}", "tagcompare", time.strftime("%Y%m%d-%H%M%S"))
    return build


if __name__ == '__main__':
    aggregate()
