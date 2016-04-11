import pytest
import os
from tagcompare import image


@pytest.mark.integration
def test_generate_diff_img():
    """
    def generate_diff_img(file1, file2, diff_img_path):
    :return:
    """
    test_assets = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "/assets"

    test_img_1 = test_assets + os.path.sep + "test1.png"
    test_img_2 = test_assets + os.path.sep + "test2.png"
    result_img = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "result.png"

    image.generate_diff_img(test_img_1, test_img_2, result_img)

    assert os.path.isfile(result_img), \
        "There should be a result image in test folder!"
    print "diff image test passed!"
    os.remove(result_img)
