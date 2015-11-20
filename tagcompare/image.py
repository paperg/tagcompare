import math
from PIL import Image
import shutil


def compare(file1, file2):
    """Compares two images and return a score for how similar they are
    http://stackoverflow.com/questions/1927660/compare-two-images-the-python-linux-way
    """
    image1 = _normalize_img(file1)
    image2 = _normalize_img(file2)
    result = _compare_img(image1, image2)
    print "comparing {} to {}:\n{}".format(file1, file2, result)
    return result


def _compare_img(img1, img2):
    h1 = img1.histogram()
    h2 = img2.histogram()
    diff_squares = [(h1[i] - h2[i]) ** 2 for i in xrange(len(h1))]
    rms = math.sqrt(sum(diff_squares) / len(h1))
    return rms


def crop(img_file, cropbox):
    img = Image.open(img_file)

    if cropbox:
        img = img.crop(cropbox)

    # backup file before saving back
    shutil.copyfile(img_file, img_file + ".bak")
    img.save(open(img_file, 'wb'))
    return img


def _normalize_img(img_file):
    # TODO: Actually do something to normalize
    return Image.open(img_file)
