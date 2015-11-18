import math
from PIL import Image
from os import path
import os
import shutil


'''
Compares two images and return a score for how similar they are
http://stackoverflow.com/questions/1927660/compare-two-images-the-python-linux-way
'''
def compare(file1, file2):
    image1 = _normalize_img(file1)
    image2 = _normalize_img(file2)
    result = _compare_img(image1, image2)
    print "comparing {} to {}:\n{}".format(file1, file2, result)
    return result


def _compare_img(img1, img2):
    h1 = img1.histogram()
    h2 = img2.histogram()
    diff_squares = [(h1[i] - h2[i]) ** 2 for i in xrange(len(h1))]
    rms = math.sqrt(sum(diff_squares) / len(h1));
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


def _n_way_compare(compare_set):
    for c in compare_set:
        cset = compare_set[c]
        #print cset

        firefox = cset['firefox']
        chrome = cset['chrome']
        ie11 = cset['ie11']
        compare(chrome, firefox)
        compare(chrome, ie11)
        compare(firefox, ie11)


def _load_files(dirpath):
    result = {}

    print("Loading files from {}...".format(dirpath))
    # Load all the things :ha:
    # Note - we are assuming the input dir is structured such that it has a bunch of folders with files to compare
    dirs = os.listdir(dirpath)
    for d in dirs:
        dpath = path.join(dirpath, d)
        if not path.isdir(dpath):
            continue

        files = os.listdir(dpath)
        for f in files:
            if not str(f).endswith(".png"):
                continue

            # fileset contains different image files with the same name across the different dirs
            fileset = {}
            fpath = path.join(dpath, f)
            if f in result:
                fileset = result[f]

            fileset[d] = fpath
            result[f] = fileset

    #print result
    return result


def compare_output_dir(dirpath):
    print ""
    print "_--==== COMPARING RESULTS ====--_"
    print ""

    if not path.exists(dirpath):
        raise ValueError('dirpath is not a valid path!')

    compare_set = _load_files(dirpath)
    _n_way_compare(compare_set)


if __name__ == '__main__':
    compare_output_dir("output/20151116-175020/")