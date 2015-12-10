import pytest

from tagcompare import placelocal


@pytest.mark.integration
def test_get_tags_for_campaigns():
    cids = [516675, 509147]
    tags, count = placelocal.get_tags_for_campaigns(cids=cids)
    assert tags, "Did not get tags for cid {}!".format(cids)
    assert count == 24, "Should have gotten exactly 24 tags!"
    for cid in tags:
        tags_per_campaign = tags[cid]
        assert len(tags_per_campaign) == 6, "Should have 6 sizes per campaign!"
        tags_per_size = tags_per_campaign['medium_rectangle']
        assert len(tags_per_size) == 2, "Should have 2 tags per size!"
        iframe_tag = tags_per_size['iframe']
        assert iframe_tag, "Should have iframe tag!"


def test_get_tags_for_campaigns_invalid():
    with pytest.raises(ValueError):
        placelocal.get_tags_for_campaigns(cids=None)


@pytest.mark.integration
def test_get_cids_from_publications():
    pub = 627
    cids = placelocal.get_cids(pids=[pub])
    assert cids, "Did not get any campaigns for publisher {}!".format(pub)
    assert len(cids) > 0, "Should have found some active campaigns!"
    print "Found {} campaigns for publisher {}".format(len(cids), pub)


def test_get_cids():
    cids = placelocal.get_cids(cids=[1, 2, 3])
    assert cids, "Could not get cids!"
    assert len(cids) == 3, "There should be exactly 3 cids!"


def test_get_cids_invalid():
    with pytest.raises(ValueError):
        placelocal.get_cids()
