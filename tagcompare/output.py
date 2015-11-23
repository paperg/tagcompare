"""Handles output files from the tagcompare tool
    - Creates output directories before a run
    - Compares the test configs with the result/output configs
    - Utility methods for getting the right path to outputs
"""
import os

import settings
import time


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
BUILDS_DIR = os.path.join(OUTPUT_DIR, 'builds')


class PathBuilder():
    """Class to store & build paths/partial paths to outputs of tagcompare
    """
    # TODO: Consider making this class immutable
    def __init__(self, config=None, cid=None, size=None, build=None):
        self.config = config
        self.cid = cid
        self.size = size

        # TODO: Fix build/buildpath - consolidate it with the way we store builds by default
        self.build = build
        if not self.build:
            self.build = generate_build_string()

    @property
    def path(self):
        return getpath(self.config, self.cid, self.size)

    def validate(self):
        return os.path.exists(self.path)

    def create(self):
        result = self.path
        if not self.validate():
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
        result = os.path.join(BUILDS_DIR, self.build)
        if not os.path.exists(result):
            os.makedirs(result)
        return result

"""
Static helper methods:
"""


def makedirs():
    """Makes output directories in the structure of:
        - config_name
            - campaign_id
                - tag_sizes
    """
    configs = settings.DEFAULT.configs
    for c in configs:
        config_dir = os.path.join(OUTPUT_DIR, c)
        campaigns = settings.DEFAULT.campaigns
        for cid in campaigns:
            cid_dir = os.path.join(config_dir, str(cid))
            sizes = settings.DEFAULT.tagsizes
            for s in sizes:
                size_dir = os.path.join(cid_dir, s)
                if os.path.exists(size_dir):
                    continue
                os.makedirs(size_dir)


def getpath(config, cid=None, size=None):
    """Gets the output path for a given config, cid and size
       Returns partial paths if optional parameters aren't provided
    """
    # Normalize inputs
    config = str(config)
    cid = str(cid)
    size = str(size)

    result = os.path.join(OUTPUT_DIR, config)
    if not cid:
        return result
    result = os.path.join(result, cid)

    if not size:
        return result

    result = os.path.join(result, size)
    return result


def generate_build_string():
    build = str.format("{}_{}", "tagcompare", time.strftime("%Y%m%d-%H%M%S"))
    return build

if __name__ == '__main__':
    makedirs()
