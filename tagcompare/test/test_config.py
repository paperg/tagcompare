import pytest
from tagcompare import config
import os
import sys


@pytest.fixture
def config_obj():
    return config.Config('config.json')


def test_config():
    t = config_obj().config
    print "config:\n{}".format(t)
    assert t, "no config object!"


def test_domain():
    t = config_obj().domain
    assert t, "domain undefined!"


def test_tagsizes():
    t = config_obj().tagsizes
    assert t, "tagsizes undefined!"
    assert len(t) > 0, "tagsizes has no values!"
