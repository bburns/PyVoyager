
# voyager: center
# put the largest object in the image in the center
# --------------------------------------------------------------------------------

import sys
import time
import argparse
import os
import fnmatch

import matplotlib.pyplot as plt
import matplotlib.image as mpim
import matplotlib.patches as patches
import numpy as np


# from scipy.ndimage import measurements, morphology
import scipy.ndimage as ndimage
import scipy.misc as misc

import voyager as v        


def get_parser():
    parser = argparse.ArgumentParser(description='Center largest object in view')
    # # parser.add_argument('query', metavar='QUERY', type=str, nargs='*', help='the question to answer')
    parser.add_argument('filespec', type=str, help='the png file(s) to process')
    # parser.add_argument('suffix', type=str, nargs='?', default='_centered',
                        # help='suffix to add to filename for output')
    parser.add_argument('prefix', type=str, nargs='?', default='centered_',
                        help='prefix to add to filename for output')
    parser.add_argument("-r", "--recurse", help="recurse through subdirectories", action="store_true")
    return parser


def main():
    
    # get arguments
    parser = get_parser()
    args = parser.parse_args()
    filespec = args.filespec
    
    for root, dirs, files in os.walk("."):
        for infile in files:
            if fnmatch.fnmatch(infile, filespec):
                
                print infile
                
                # center_image_file(infile, outfile)
                
                im = mpim.imread(infile) # load image
                # im = np.rot90(im, 2) # rotate by 180
                
                
                # sums = np.sum(im, axis=0)
                # # sums = np.sum(im, axis=1)
                # diff = np.diff(sums)
                # diffsq = np.square(diff)
                # diffsqln = np.log(diffsq)
                # N=5
                # smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
                # # icenter = v.find_center_1d(smoothed, 0)
                # plt.figure(1)
                # plt.subplot(2,1,1)
                # plt.plot(diffsqln)
                # plt.subplot(2,1,2)
                # plt.plot(smoothed)
                # plt.show()
                
                imcrop = v.center_image(im, True)

                # draw crosshairs
                imcrop[399, 0:799] = 0.5
                imcrop[0:799, 399] = 0.5
                
                outfile = args.prefix + infile
                misc.imsave(outfile, imcrop)


                
if __name__ == '__main__':
    main()


