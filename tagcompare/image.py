import math
from PIL import Image
from PIL import ImageDraw
import shutil

import logger


LOGGER = logger.Logger(__name__).get()


def compare(file1, file2):
    image1 = normalize_img(file1)
    image2 = normalize_img(file2)

    result = _compare_img(image1, image2)
    LOGGER.debug("compare_img result: %s", result)
    if result is False:
        # TODO: Validate image size and normalize them
        LOGGER.error("image compare failed! (%s) <> (%s)", file1, file2)
    return result


def add_label(image, label):
    """
    :param image: The PIL.Image object to add label text to
    :param label: A text label
    :return: the image with the label added to it at the top left
    """
    draw = ImageDraw.Draw(image)
    draw.text(xy=(3, 3), fill=(0, 0, 255), text=label)
    return image


def add_info(image, info):
    """
    :param image: The PIL.Image object to add info text to
    :param info: A set of label:text objects. i.e.
        { "name": "image1", "diff": "99" }
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
        LOGGER.debug("drawing text %s at %s,%s", text, x, y)
        draw.text(xy=(x, y), fill=(255, 255, 255), text=text)
    return result


def _compare_img(img1, img2):
    """Compares two images and return a score for how similar they are
    http://stackoverflow.com/questions/1927660/
    """
    h1 = img1.histogram()
    h2 = img2.histogram()
    if (len(h1) > len(h2)):
        return False

    diff_squares = [(h1[i] - h2[i]) ** 2 for i in xrange(len(h1))]
    rms = math.sqrt(sum(diff_squares) / len(h1))
    return int(rms)


def crop(img_file, cropbox, backup=False):
    img = Image.open(img_file)

    if cropbox:
        # TODO: validate cropbox within image
        img = img.crop(cropbox)

    if backup:
        # backup file before saving back
        shutil.copyfile(img_file, img_file + ".bak")
    img.save(open(img_file, 'wb'))
    return img


def normalize_img(img_file, greyscale=False):
    img = Image.open(img_file)
    if not greyscale:
        return img

    # TODO: Figure out ways to make font issues more prominent
    # greyscale
    return img.convert('LA')


def blank_compare_matrix(num_configs, width, height):
    return Image.new("RGBA", (num_configs*width, num_configs*height), (0, 0, 0, 0))


def get_overlay_mask(width, height, alpha):
    return Image.new("L", (width, height), alpha)


def draw_reference_copy(canvas, srcimg, position):
    canvas.paste(srcimg, box=position)


def _get_color_distance(px1, px2):
    # Using L2 distance on RGB space as rough approximation of "color distance"
    # Works with any length pixel as long as px1 and px2 are same tuple format.
    # Don't have to normalize the result because there has to be a normalization
    # pass at the end anyway.
    return math.sqrt(sum([abs(a-b)**2 for (a, b) in zip(px1, px2)]))


# In R8G8B8A8 space, this is white vs. black, so all distances must be at most this.
_DIST_MAX = 2*256


def draw_visual_diff(canvas, img1, img2, position, cfgstring, overlay_mask):
    # Algorithm computes "color distance" between matching pixels, then normalizes the
    # output. This makes the "diff operator" commutative, but we want to overlay the
    # "diff" against img1 so that you can see semantically what part of the image was
    # different.
    min_dist = _DIST_MAX
    max_dist = 0.0
    distances = Image.new("F", img1.size, 0.0)
    for y in range(img1.height):
        for x in range(img1.width):
            pixel = (x, y)
            color_distance = _get_color_distance(img1.getpixel(pixel),
                                                 img2.getpixel(pixel))
            distances.putpixel(pixel, color_distance)
            min_dist = min(min_dist, color_distance)
            max_dist = max(max_dist, color_distance)

    # Now normalize the distances and label it. 1.0 choice is arbitrary.
    dist_multiplier = 1.0
    # Avoids a divide by 0. If the distance on a 3-channel image with 255 pixels
    # is less than one tenth of a color step, then they're effectively identical images,
    # so there's no point in normalizing.
    if (max_dist - min_dist > 0.1):
        dist_multiplier = 255.0/(max_dist-min_dist)
    # Only need luminance channel since it's a 1-d distance metric.
    normalized_distances = Image.new("L", img1.size, 0)
    for y in range(img1.height):
        for x in range(img1.width):
            pixel = (x, y)
            # Safe to cast to int because dist_multiplier * (pixel - pixel_min) should
            # never exceed 255, and it's 256 we're worried about.
            normalized_dist = int(dist_multiplier * (distances.getpixel(pixel)-min_dist))
            normalized_distances.putpixel(pixel, normalized_dist)

    # Draw base image, then draw diff on top.
    draw_reference_copy(canvas=canvas, srcimg=img1, position=position)
    # and then paint the "difference magnitudes"
    canvas.paste(normalized_distances, position, overlay_mask)
    # and finally label what the comparison is for.
    draw = ImageDraw.Draw(canvas)
    draw.text(xy=(position[0]+3, position[1]+3), fill=(0, 0, 255), text=cfgstring)
