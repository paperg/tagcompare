import json
import os


DEFAULT_FILENAME = "settings.json"
DEFAULT_LOCAL_FILENAME = "settings.local.json"


class Settings():
    """The configuration class for tagcompare.
    reads settings.py and provides setting values to consumers
    """

    def __init__(self, configfile=DEFAULT_LOCAL_FILENAME):
        configfile_path = _get_abs_path(configfile)

        if not os.path.exists(configfile_path):
            # Use default config file if no override
            configfile_path = _get_abs_path(DEFAULT_FILENAME)

        self.__configfile = configfile_path
        self.__settings = None
        self.__compare_set = None


    @property
    def _settings(self):
        if self.__settings:
            return self.__settings

        assert self.__configfile, "No config file specified!"
        assert os.path.exists(self.__configfile), "Settings file not found at {}".format(self.__configfile)
        self.__settings = json.load(open(self.__configfile, "r"))
        return self.__settings

    @property
    def domain(self):
        return self.placelocal['domain']

    @property
    def tagsizes(self):
        return self._settings['tagsizes']

    @property
    def campaigns(self):
        return self._settings['campaigns']

    @property
    def publishers(self):
        return self._settings['publishers']

    @property
    def webdriver(self):
        """Gets the remote webdriver settings to use
            saucelabs: https://wiki.saucelabs.com/display/DOCS/Platform+Configurator#/
            browserstack: https://www.browserstack.com/list-of-browsers-and-platforms?product=automate
        """
        webdriver_profiles = self._settings['webdriver']
        for name in webdriver_profiles:
            if webdriver_profiles[name]['enabled']:
                return webdriver_profiles[name]
        raise ValueError("No webdriver profile is marked as enabled!")

    @property
    def placelocal(self):
        return self._settings['placelocal']

    @property
    def _compare_set(self):
        """Loads compare.json and
        :return: the set of comparisons and configs from config.json
        """
        if self.__compare_set:
            return self.__compare_set

        self.__compare_set = _load_json_file("compare.json")
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
        tmpset = {}
        for comp in self.comparisons:
            complist = self.comparisons[comp]
            tmpset = set(tmpset).union(set(complist))

        unique_configs = list(tmpset)
        return unique_configs


def _get_abs_path(relpath):
    dirpath = os.path.abspath(os.path.dirname(__file__))
    abspath = os.path.join(dirpath, relpath)
    return abspath


def _load_json_file(relpath):
    return json.load(open(_get_abs_path(relpath), "r"))


# TODO: not sure if this is proper...
DEFAULT = Settings()
