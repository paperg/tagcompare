import pytest

from tagcompare import placelocal


@pytest.mark.integration
def test_get_tags_for_campaigns():
    cids = [516675, 509147]
    tags, count = placelocal.get_tags_for_campaigns(cids=cids)
    assert tags, "Did not get tags for cid {}!".format(cids)
    print "Found {} tags for cid {}.".format(count, cids)


@pytest.mark.integration
def test_get_active_campaigns():
    pub = 627
    cids = placelocal.get_active_campaigns(pid=pub)
    assert cids, "Did not get any campaigns for publisher {}!".format(pub)
    print "Found {} campaigns for publisher {}".format(len(cids), pub)


def test_get_cids():
    cids = placelocal.get_cids(cids=[1, 2, 3])
    assert cids, "Could not get cids!"
    assert len(cids) == 3, "There should be exactly 3 cids!"


def test_get_cids_invalid():
    with pytest.raises(ValueError):
        placelocal.get_cids()
