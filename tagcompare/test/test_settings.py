from tagcompare import settings


SETTINGS = settings.Settings(configfile='test/test_settings.json',
                             comparefile='test/test_compare.json')


def test_config():
    t = SETTINGS._settings
    print "config:\n{}".format(t)
    assert t, "no settings object!"


def test_domain():
    t = SETTINGS.domain
    assert t, "domain undefined!"


def test_tagsizes():
    t = SETTINGS.tagsizes
    assert t, "tagsizes undefined or have no values!"


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
