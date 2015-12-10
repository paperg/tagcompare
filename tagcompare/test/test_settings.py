import tempfile
import os

from tagcompare import settings


settings.TEST_MODE = True
TEST_COMPARE_FILE = 'test/assets/test_compare.json'
TEST_SETTINGS_FILE = 'test/assets/test_settings.json'
SETTINGS = settings.Settings(configfile=TEST_SETTINGS_FILE,
                             comparefile=TEST_COMPARE_FILE)


def test_config():
    t = SETTINGS._settings
    print "config:\n{}".format(t)
    assert t, "no settings object!"


def test_domain():
    t = SETTINGS.domain
    assert t, "domain undefined!"


def __test_logdir(logdir):
    assert logdir, "Could not get logdir!"
    assert os.path.exists(logdir), "logdir was not created on init!"


def test_logdir():
    tmpdir = tempfile.gettempdir()
    s = settings.Settings(configfile=TEST_SETTINGS_FILE,
                          comparefile=TEST_COMPARE_FILE,
                          logdir=tmpdir)
    __test_logdir(s.logdir)
    newdir = "new_logdir"
    s = settings.Settings(configfile=TEST_SETTINGS_FILE,
                          comparefile=TEST_COMPARE_FILE,
                          logdir=newdir)
    __test_logdir(s.logdir)
    os.rmdir(s.logdir)


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
    assert len(all_types) == 3, "There should be exactly 4 supported types!"
    enabled_types = SETTINGS.tagtypes
    assert len(enabled_types) == 1, "There should be exactly 1 enabled types!"


def test_saucelabs():
    sauce_settings = SETTINGS._saucelabs
    assert sauce_settings, "Could not get saucelabs settings!"
    user = SETTINGS.get_saucelabs_user(env=None)
    assert user == "TEST_USER", "Did not read sauce user from JSON!"
    key = SETTINGS.get_saucelabs_key(env=None)
    assert key == "TEST_KEY", "Did not read sauce key from JSON!"

    # test env override (default behavior) if env vars are set
    expected_user = os.environ.get(settings.Env.SAUCE_USER)
    expected_key = os.environ.get(settings.Env.SAUCE_KEY)
    print "\n\n\nDEBUG:" + str(expected_key)  # TODO
    if expected_user:
        user = SETTINGS.get_saucelabs_user()
        assert user == expected_user, "Did not get sauce user from env!"
    if expected_key:
        key = SETTINGS.get_saucelabs_key()
        assert key == expected_key, "Did not get sauce key from env!"


def test_get_placelocal_headers():
    headers1 = SETTINGS.get_placelocal_headers(id_env=None, secret_env=None)
    expected_headers = {
        "pl-secret": "SECRET",
        "pl-service-identifier": "ID"
    }
    assert headers1 == expected_headers

    os.environ[settings.Env.PL_SECRET] = 'SECRET'
    os.environ[settings.Env.PL_SERVICE_ID] = 'ID'
    # Get headers from env
    headers2 = SETTINGS.get_placelocal_headers()
    assert headers2 == headers1


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
