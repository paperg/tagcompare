import os
import logging

from tagcompare import settings

settings.TEST_MODE = True
TEST_COMPARE_FILE = 'test/assets/test_compare.json'
TEST_SETTINGS_FILE = 'test/assets/test_settings.json'
TEST_LOGS_DIR = 'test/assets/logs/'


def createSettings(configfile=TEST_SETTINGS_FILE,
                   comparefile=TEST_COMPARE_FILE,
                   logdir=TEST_LOGS_DIR, validate=False):
    test_settings = settings.Settings(configfile, comparefile, logdir)

    if validate:
        assert configfile in test_settings._configfile
        assert test_settings._comparefile == comparefile
        assert logdir in test_settings.logdir
    return test_settings


SETTINGS = createSettings(validate=True)


def test_domain():
    domain_settings = createSettings()
    assert domain_settings.domain == "www.placelocal.com", \
        "Default domain is not correct!"
    expected_domain = "www.example.com"
    domain_settings.domain = expected_domain
    assert domain_settings.domain == expected_domain, "domain was not set correctly!"


def test_campaigns():
    test_settings = createSettings()
    assert test_settings.campaigns == [131313], \
        "Default campaigns is not correct!"
    expected = [999999]
    test_settings.campaigns = expected
    assert test_settings.campaigns == expected, "campaigns was not set correctly!"


def test_publishers():
    test_settings = createSettings()
    assert test_settings.publishers == [627], \
        "Default publishers is not correct!"
    expected = [444]
    test_settings.publishers = expected
    assert test_settings.publishers == expected, "publishers was not set correctly!"


def test_loglevel():
    test_settings = createSettings()
    assert test_settings.loglevel == logging.INFO, \
        "Default loglevel is not correct!"
    expected = logging.DEBUG
    test_settings.loglevel = expected
    assert test_settings.loglevel == expected, "loglevel was not set correctly!"


def test_config():
    t = SETTINGS._settings
    print "config:\n{}".format(t)
    assert t, "no settings object!"


def __test_logdir(logdir, expected):
    assert logdir, "Could not get logdir!"
    assert expected in logdir, "logdir value is not expected!"
    assert os.path.exists(logdir), "logdir does not exist!"


def test_logdir():
    tmpdir = "new_logs_dir"
    s = createSettings(configfile=TEST_SETTINGS_FILE,
                       comparefile=TEST_COMPARE_FILE,
                       logdir=tmpdir)
    __test_logdir(s.logdir, tmpdir)
    os.rmdir(s.logdir)


def test_invalid_configfile():
    s = createSettings(configfile='invalid/path', validate=False)
    configs = s.all_configs
    assert configs, "Should have gotten default configs!"


def test_tagsizes():
    test_tag_settings = createSettings()
    tag_settings = test_tag_settings.tag
    assert tag_settings, "Could not get tag settings!"
    all_sizes = tag_settings['sizes']
    assert all_sizes, "Could not get sizes from tag settings!"
    assert len(all_sizes) == 4, "There should be exactly 4 supported sizes!"
    enabled_sizes = test_tag_settings.tagsizes
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


def test_saucelabs():
    new_settings = createSettings()
    sauce_settings = new_settings._saucelabs
    assert sauce_settings, "Could not get saucelabs settings!"
    user = new_settings.get_saucelabs_user(env=None)
    assert user == "TEST_USER", "Did not read sauce user from JSON!"
    key = new_settings.get_saucelabs_key(env=None)
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
    t = SETTINGS.all_configs
    assert t, "configs undefined or have no values!"


def test_comparisons():
    t = SETTINGS.comparisons
    assert t, "comparisons undefined or have no values!"


def test_all_comparisons():
    t = SETTINGS.all_comparisons
    assert t, "all_comparisons undefined or have no values!"


def test_comparisons_matches_configs():
    configs = SETTINGS.all_configs

    # Check that all the unique values in comparisons are specified in configs
    unique_configs = SETTINGS.configs_in_comparisons()
    for c in unique_configs:
        assert c in configs
