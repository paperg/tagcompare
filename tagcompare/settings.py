import json
import os
import logging

from enum import IntEnum


MODULE_NAME = "tagcompare"
DEFAULT_FILENAME = "settings.json"
DEFAULT_LOCAL_FILENAME = "settings.local.json"
DEFAULT_COMPARE_FILENAME = "compare.json"

OUTPUT_DIR = os.path.join("/tmp/", MODULE_NAME)
LOG_LEVEL = logging.INFO


class Test:
    TEST_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "test"))
    TEST_ASSETS_DIR = os.path.join(TEST_DIR, "assets")


class ImageErrorThreshold(IntEnum):
    NONE = 0,
    SLIGHT = 100,
    MODERATE = 250,
    BAD = 500,
    SEVERE = 1000


class Env:
    SAUCE_USER = "SAUCE_USER"
    SAUCE_KEY = "SAUCE_KEY"
    PL_SECRET = "PL_SECRET"
    PL_SERVICE_ID = "PL_SERVICE_ID"

# Used by tests to access special conditions
TEST_MODE = False

"""
The animation time until the tag stops on the final frame
Setting animation time of 1 makes the ad transition to final frame after 1s
Any lower than this will cause incorrect animation transitions on the final frame
"""
TAG_ANIMATION_TIME = 1

""" Helper methods """


def get_unique_configs_from_comparisons(comparisons):
    tmpset = {}
    for comp in comparisons:
        complist = comparisons[comp]
        tmpset = set(tmpset).union(set(complist))

    unique_configs = list(tmpset)
    return unique_configs


def _get_enabled_items_in_dict(dictionary):
    return [item for item in dictionary if dictionary[item]]


def _get_abs_path(relpath):
    dirpath = os.path.abspath(os.path.dirname(__file__))
    abspath = os.path.join(dirpath, relpath)
    return abspath


def _load_json_file(relpath):
    return json.load(open(_get_abs_path(relpath), "r"))


class Settings():
    """The configuration class for tagcompare.
    reads settings.py and provides setting values to consumers
    """

    def __init__(self, configfile=DEFAULT_LOCAL_FILENAME,
                 comparefile=DEFAULT_COMPARE_FILENAME, logdir=OUTPUT_DIR):
        configfile_path = _get_abs_path(configfile)

        self.__logdir = _get_abs_path(logdir)
        if not os.path.exists(self.__logdir):
            os.makedirs(self.__logdir)

        if not os.path.exists(configfile_path):
            self.__configfile = _get_abs_path(DEFAULT_FILENAME)
            logging.warn(
                "Invalid configfile_path (%s), using default file at %s",
                configfile_path, self.__configfile)
        else:
            self.__configfile = configfile_path
        self.__settings = None
        self.__comparefile = comparefile
        self.__compare_set = None

    @property
    def logdir(self):
        return self.__logdir

    @property
    def _settings(self):
        if self.__settings:
            return self.__settings

        assert self.__configfile, "No config file specified!"
        assert os.path.exists(self.__configfile), \
            "Settings file not found at {}".format(self.__configfile)
        self.__settings = json.load(open(self.__configfile, "r"))
        return self.__settings

    @property
    def domain(self):
        return self._placelocal['domain']

    @property
    def tag(self):
        return self.__settings['tag']

    @property
    def tagsizes(self):
        return _get_enabled_items_in_dict(self.tag['sizes'])

    @property
    def tagtypes(self):
        return _get_enabled_items_in_dict(self.tag['types'])

    @property
    def campaigns(self):
        return self._settings['campaigns']

    @property
    def publishers(self):
        return self._settings['publishers']

    @property
    def _saucelabs(self):
        return self._settings['saucelabs']

    @property
    def _placelocal(self):
        return self._settings['placelocal']

    @property
    def _compare_set(self):
        """Loads compare.json and
        :return: the set of comparisons and configs from config.json
        """
        if self.__compare_set:
            return self.__compare_set

        self.__compare_set = _load_json_file(self.__comparefile)
        return self.__compare_set

    @property
    def comparisons(self):
        return self._compare_set['comparisons']

    @property
    def configs(self):
        return self._compare_set['configs']

    def configs_in_comparison(self):
        """Gets a list of unique configs from the comparisons matrix
        :return:
        """
        return get_unique_configs_from_comparisons(self.comparisons)

    def get_saucelabs_user(self, env=Env.SAUCE_USER):
        value = os.environ.get(env)
        if value:
            return value
        return self._saucelabs['user']

    def get_saucelabs_key(self, env=Env.SAUCE_KEY):
        value = os.environ.get(env)
        if value:
            return value
        return self._saucelabs['key']

    def get_placelocal_headers(self,
                               id_env=Env.PL_SERVICE_ID,
                               secret_env=Env.PL_SECRET):
        id = os.environ.get(id_env)
        secret = os.environ.get(secret_env)
        if id and secret:
            headers = {
                "pl-secret": secret,
                "pl-service-identifier": id
            }
            return headers
        headers = self._placelocal['secret']
        print("get_placelocal_headers: %s" % headers)
        return headers


# TODO: not sure if this is proper...
DEFAULT = Settings()
