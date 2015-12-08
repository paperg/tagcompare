import tempfile
import os

import pytest

from tagcompare import settings


settings.TEST_MODE = True
SETTINGS = settings.Settings(configfile='test/test_settings.json',
                             comparefile='test/test_compare.json')


def test_config():
    t = SETTINGS._settings
    print "config:\n{}".format(t)
    assert t, "no settings object!"


def test_domain():
    t = SETTINGS.domain
    assert t, "domain undefined!"


def test_logdir():
    tmpdir = tempfile.gettempdir()
    s = settings.Settings(configfile='test/test_settings.json',
                          comparefile='test/test_compare.json',
                          logdir=tmpdir)
    logdir = s.logdir
    assert logdir, "Could not get logdir!"
    assert os.path.exists(logdir), "logdir was not created on init!"


def test_invalid_configfile():
    s = settings.Settings(configfile='invalid/path')
    configs = s.configs
    assert configs, "Should have gotten default configs!"


def test_tagsizes():
    tag_settings = SETTINGS.tag
    assert tag_settings, "Could not get tag settings!"
    all_sizes = tag_settings['sizes']
    assert all_sizes, "Could not get sizes from tag settings!"
    assert len(all_sizes) == 4, "There should be exactly 4 supported sizes!"
    enabled_sizes = SETTINGS.tagsizes
    assert enabled_sizes, "Could not get enabled_sizes from tag settings"
    assert "medium_rectangle" in enabled_sizes, "medium_rectangle should be enabled!"
    assert "skyscraper" not in enabled_sizes, "skyscraper should not be enabled!"
    assert len(enabled_sizes) == 3, "There should be exactly 3 enabled sizes!"


def test_tagtypes():
    tag_settings = SETTINGS.tag
    assert tag_settings, "Could not get tag settings!"
    all_types = tag_settings['types']
    assert all_types, "Could not get types from tag settings!"
    assert len(all_types) == 2, "There should be exactly 4 supported types!"
    enabled_types = SETTINGS.tagtypes
    assert len(enabled_types) == 1, "There should be exactly 1 enabled types!"


def test_webdriver():
    webdriver_settings = SETTINGS.webdriver
    assert webdriver_settings, "Could not get webdriver settings!"
    invalid = settings.Settings(configfile='test/test_settings_invalid.json')
    with pytest.raises(ValueError):
        print "This should raise ValueError: %s" % invalid.webdriver


def test_configs():
    t = SETTINGS.configs
    assert t, "configs undefined or have no values!"


def test_comparisons():
    t = SETTINGS.comparisons
    assert t, "comparisons undefined or have no values!"


def test_comparisons_matches_configs():
    configs = SETTINGS.configs

    # Check that all the unique values in comparisons are specified in configs
    unique_configs = SETTINGS.configs_in_comparison()
    for c in unique_configs:
        assert c in configs
