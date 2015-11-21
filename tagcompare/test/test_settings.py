import pytest

from tagcompare import settings


CONFIG = settings.Settings('config.json')


def test_config():
    t = CONFIG._settings
    print "config:\n{}".format(t)
    assert t, "no settings object!"


def test_domain():
    t = CONFIG.domain
    assert t, "domain undefined!"


def test_tagsizes():
    t = CONFIG.tagsizes
    assert t, "tagsizes undefined or have no values!"


def test_configs():
    t = CONFIG.configs
    assert t, "configs undefined or have no values!"


def test_comparisons():
    t = CONFIG.comparisons
    assert t, "comparisons undefined or have no values!"


def test_comparisons_matches_configs():
    configs = CONFIG.configs

    # Check that all the unique values in comparisons are specified in configs
    unique_configs = CONFIG.configs_in_comparison()
    for c in unique_configs:
        assert c in configs

