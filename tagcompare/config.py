import json
import os


class Config():
    """The configuration class for tagcompare.
    reads config.py and provides config options to consumers
    """

    def __init__(self, configfile="config.local.json"):
        dirpath = os.path.abspath(os.path.dirname(__file__))
        configfile_path = os.path.join(dirpath, configfile)

        if not os.path.exists(configfile_path):
            # Use default config file if no override
            configfile_path = os.path.join(dirpath, "config.json")

        self.__configfile = configfile_path
        self.__config = None

    @property
    def config(self):
        if self.__config:
            return self.__config

        assert self.__configfile, "No config file specified!"
        assert os.path.exists(self.__configfile), "Config file not found at {}".format(self.__configfile)
        self.__config = json.load(open(self.__configfile, "r"))
        return self.__config

    @property
    def domain(self):
        return self.placelocal['domain']

    @property
    def tagsizes(self):
        return self.config['tagsizes']

    @property
    def campaigns(self):
        return self.config['campaigns']

    @property
    def publishers(self):
        return self.config['publishers']

    @property
    def webdriver(self):
        return self.config['webdriver']

    @property
    def placelocal(self):
        return self.config['placelocal']


DEFAULT = Config()
