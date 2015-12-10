import os

import pytest

from tagcompare import settings
from tagcompare import capture
from tagcompare import compare


# TODO: Make it work without having local secret file
SETTINGS = settings.Settings(comparefile='test/assets/test_compare.json')


@pytest.mark.integration
def test_end_to_end():
    cids = [477944]
    build = "test_e2e_build"
    capture.main(cids=cids, build=build)
    pb = compare.main(jobname=build)
    assert os.path.exists(pb.buildpath)
    pb.rmbuild()
