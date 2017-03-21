#!/usr/bin/env python

import os
import glob
import optparse
import numpy
#import Image
from PIL import Image
#import leargist
import cPickle

class Dataset:
    # Create an empty dataset
    def __init__(self):
        self.dataset = ()

    # Build a dataset from imagedir
    def build(self, imagedir):
        # Get number of samples per family
        os.chdir(imagedir)  # the parent folder with sub-folders
        list_fams = sorted(os.listdir(os.getcwd()), key=str.lower)  # vector of strings with family names
        no_imgs = []  # No. of samples per family
        for i in range(len(list_fams)):
            os.chdir(list_fams[i])
            len1 = len(glob.glob('*.png'))  # assuming the images are stored as 'png'
            no_imgs.append(len1)
            os.chdir('..')
        total = sum(no_imgs)  # total number of all samples

        # Compute the labels
        y = numpy.zeros(total)
        pos = 0
        label = 0
        for i in no_imgs:
            print("Label:%d\tFamily: %s\tNumber of images: %d" % (label, list_fams[label], i))
            for j in range(i):
                y[pos] = label
                pos += 1
            label += 1

        # Compute the features
        X = numpy.zeros((sum(no_imgs), 320))
        #X = numpy.zeros((sum(no_imgs), 224*224))
        cnt = 0
        for i in range(len(list_fams)):
            os.chdir(list_fams[i])
            img_list = glob.glob('*.png')
            for j in range(len(img_list)):
                print("[%d] Processing image: %s" % (cnt, img_list[j]))
                im = Image.open(img_list[j])
                im1 = im.resize((64, 64), Image.ANTIALIAS)
                des = leargist.color_gist(im1)
                X[cnt] = des[0:320]
                #im1 = im.resize((224, 224), Image.ANTIALIAS)
                #des = numpy.array(im1.getdata(),numpy.uint8).reshape(224*224)
                #X[cnt] = des[:]
                cnt += 1
            os.chdir('..')
        os.chdir('..')

        # Create dataset as a tuple (X, y, list_fams)
        self.dataset = (X, y, list_fams, no_imgs)

    # Save dataset to output file
    def save(self, outputfile):
        f = open(outputfile, 'wb')
        cPickle.dump(self.dataset, f)
        f.close()

    # Load dataset from input file
    def load(self, inputfile):
        f = open(inputfile, 'rb')
        self.dataset = cPickle.load(f)
        f.close()
        return self.dataset

    # Get current dataset
    def get(self):
        return self.dataset


    # Show current dataset
    def show(self):
        print(self.dataset)


if __name__ == '__main__':
    usage = 'Usage: %prog -d featuredir -f outputfile'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-d', '--dir', action="store", type="string", dest="imagedir",
                      help='directory containing image files')
    parser.add_option('-f', '--file', action="store", type="string", dest="outputfile",
                      help='set output file to write the dataset')
    (options, args) = parser.parse_args()
    if not options.imagedir:
        parser.error('missing option: -d imagedir')
    if not options.outputfile:
        parser.error('missing option: -f outputfile')

    dataset = Dataset()
    print("Building dataset: %s" % (options.imagedir))
    dataset.build(options.imagedir)
    print("Dataset:")
    dataset.show()
    print("Saving dataset to file: %s" % (options.outputfile))
    dataset.save(options.outputfile)
