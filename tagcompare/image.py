import math
from PIL import Image
from PIL import ImageDraw
import shutil

ERROR_THRESHOLD = 300


def compare(file1, file2):
    image1 = normalize_img(file1)
    image2 = normalize_img(file2)

    try:
        result = _compare_img(image1, image2)
    except IndexError:
        print("compare failed for {} to {} due to index error".format(file1, file2))
        return False
    # print "comparing {} to {}:\n{}".format(file1, file2, result)
    return result


def merge_images(file1, file2):
    """Merge two images into one, displayed side by side
    :param file1:
    :param file2:
    :return:
    """
    image1 = normalize_img(file1)
    image2 = normalize_img(file2)

    (width, height) = image1.size
    result_width = width * 2
    result_height = height

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width, 0))
    return result


def add_info(image, info):
    """
    :param image: The PIL.Image object to add info text to
    :param info: A set of label:text objects. i.e. { "name": "image1", "diff": "99" }
    :return: the image with the additional info added to it
    """
    (original_width, original_height) = image.size
    line_height = 20
    extra_height = (len(info) + 2) * line_height
    result = Image.new('RGB', (original_width, original_height + extra_height))
    result.paste(im=image, box=(0, 0))
    draw = ImageDraw.Draw(result)

    y = original_height
    for key in info:
        value = info[key]
        x = line_height
        y += line_height
        text = "{}: {}".format(key, value)
        # print "drawing text {} at {},{}".format(text, x, y)
        draw.text(xy=(x, y), fill=(255, 255, 255), text=text)
    return result


def _compare_img(img1, img2):
    """Compares two images and return a score for how similar they are
    http://stackoverflow.com/questions/1927660/compare-two-images-the-python-linux-way
    """
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


def normalize_img(img_file, greyscale=False):
    img = Image.open(img_file)
    if not greyscale:
        return img

    # greyscale
    return img.convert('LA')
