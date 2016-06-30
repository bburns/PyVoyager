
# pyvoyager
# voyager image manipulation routines
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

    
        
#. what if blobs is empty?
def find_largest_blob(blobs):
    widthmax = 0
    heightmax = 0
    for blob in blobs:
        width = blob[0].stop - blob[0].start
        height = blob[1].stop - blob[1].start
        if width>widthmax and height>heightmax:
            widthmax = width
            heightmax = height
            largest = blob
    return largest
    

def find_edges_1d(a, epsilon = 0):
    "find edges > epsilon in 1d array from left and right directions"
    icount = len(a)
    i1 = 0
    # for i in xrange(icount):
    istart = 4
    iend = icount
    for i in xrange(istart, iend, 1):
        if a[i] > epsilon:
            i1 = i
            break
    i2 = 0
    # for i in xrange(icount-1, -1, -1):
    for i in xrange(iend-1, istart-1, -1):
        if a[i] > epsilon:
            i2 = i
            break
    # icenter = (i1+i2)/2
    # print i1,i2, icenter
    # return icenter
    return i1,i2


def find_edges_2d(im, axis, epsilon=0, N=5):
    "Find the edges for the given axis"
    sums = np.sum(im, axis=axis)
    diff = np.diff(sums)
    diffsq = np.square(diff)
    diffsqln = np.log(diffsq)
    if N>0:
        smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
        i1, i2 = find_edges_1d(smoothed, epsilon)
    else:
        i1, i2 = find_edges_1d(diffsqln, epsilon)
    return i1, i2                


def find_object_edges(im, epsilon=0, N=5):
    "find edges of largest object in image based on the most prominent edges"
    x1, x2 = find_edges_2d(im, 1, epsilon, N)
    y1, y2 = find_edges_2d(im, 0, epsilon, N)
    return x1,x2,y1,y2
    

def find_center_by_blob(im):
    
    b = 1*(im>0.1) # threshold to binary image
    lbl, nobjs = ndimage.measurements.label(b) # label objects

    # find position of objects - index is 0-based
    blobs = ndimage.find_objects(lbl)

    if len(blobs)>0:
        
        # find largest object
        blob = find_largest_blob(blobs)

        # get center of blob
        cx = (blob[0].start + blob[0].stop) / 2
        cy = (blob[1].start + blob[1].stop) / 2

    else:
        cx = im.shape[0]/2
        cy = im.shape[1]/2
        
    return cx,cy


def center_image(im, drawBox):
    "center image on largest object in it, crop to it"
    
    # cx, cy = find_center_by_blob(im)
    # cx, cy = find_center_by_edges(im)
    x1,x2,y1,y2 = find_object_edges(im)
    cx = (x1+x2)/2.0
    cy = (y1+y2)/2.0
    # draw bounding box
    c = 0.5
    im[x1:x2,y1] = c
    im[x1:x2,y2] = c
    im[x1,y1:y2] = c
    im[x2,y1:y2] = c
    
    imwidth = im.shape[0]
    imheight = im.shape[1]
    
    # make a bigger canvas to place image im on
    newsize = (imwidth * 2, imheight * 2)
    canvas = np.zeros(newsize)
    
    # put image on canvas centered on blob
    # eg canvas[800-cx:1600-cx, 800-cy:1600-cy] = np.array(im)
    canvas[imwidth-cx : imwidth-cx+imwidth, imheight-cy : imheight-cy+imheight] = np.array(im)

    # crop canvas to original image size
    # eg imcrop = canvas[400:1200, 400:1200]
    imcrop = canvas[imwidth/2 : imwidth/2+imwidth, imheight/2 : imheight/2+imheight]
    
    return imcrop


def drawbox(x1,x2,y1,y2):
    "Draw a box on current image"
    plt.gca().add_patch(patches.Rectangle((y1,x1), y2-y1, x2-x1, fill=False, edgecolor="green", linewidth=0.5))

    
if __name__ == '__main__':
    main()

