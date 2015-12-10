import pytest
import os

from tagcompare import capture
from tagcompare import webdriver
from tagcompare import output


@pytest.mark.integration
def test_capture_preview_override():
    __test_capture_preview(True)


@pytest.mark.integration
def test_capture_preview_dont_override():
    __test_capture_preview(False)


def __test_capture_preview(override):
    """
    Verify that we can render the previews
    :param override:
    :return:
    """
    pb = output.create(build="capture_tag_test", config="testconfig", cid="testcid",
                       tagsize="leaderboard", tagtype="preview")
    capabilities = {
        "platform": "Windows 7",
        "browserName": "firefox"
    }
    driver = webdriver.setup_webdriver(capabilities)
    result = capture.__capture_preview(pathbuilder=pb,
                                       driver=driver,
                                       capture_existing=override)
    driver.quit()
    assert result is not None, "Could not capture tags!"
    assert result is not False, "Tag capture skipped!"
    assert len(result) == 0, "Errors while capturing preview!"
    assert os.path.exists(pb.tagimage), "tagimage was not captured!"
    assert os.path.exists(pb.taghtml), "taghtml was not captured!"
    pb.rmbuild()
