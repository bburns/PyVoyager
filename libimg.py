
# image processing routines


import matplotlib.image as mpim # for imread
import scipy.misc as misc # for imsave
import numpy as np # for zeros, array, copy

import cv2

#. cheating for now
import config


def findCircle(infile):
    "find best? circle in given image/file"
    circles = findCircles(infile)
    if circles!=None:
        circle = circles[0]
        return circle # (x,y,r)
    else:
        return None

    
# def findCircles(infile):
def findCircles(im):
    "find circles in the given image/file"
    
    im = cv2.imread(infile)

    # rotate 180deg
    # im = cv2.imread(infile, 0) # ,0=bw?
    # rows, cols = im.shape
    # M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
    # im = cv2.warpAffine(im, M, (cols, rows))

    # output = im.copy()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    dp = 1.2 # size of parameter space relative to input image
    minDist = 1000 # distance between circles
    # minDist = 1 # distance between circles
    param1=0.1
    param2=200
    minRadius=10
    maxRadius=100
    # maxRadius=18 # too big
    # maxRadius=17 # too small
    circles = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT,
                               dp, minDist, param1, param2, minRadius, maxRadius)
    if circles is not None:
        circles = np.round(circles[0,:]).astype('int')
        # circle = circles[0]
        # return circle # (x,y,r)
        return circles # array of (x,y,r)
    else:
        return None
    



def centerImageFile(infile, outfile, rotateImage=False):
    "center the given image file on a planet"
    im = mpim.imread(infile)
    if rotateImage:
        im = np.rot90(im, 2) # rotate by 180
    if config.centerMethod=='blob':
        boundingBox = findCenterByBlob(im)
    elif config.centerMethod=='box':
        boundingBox = findCenterByBox(im)
    elif config.centerMethod=='all':
        boundingBox = findBoundingBox(im)
    if config.drawBoundingBox:
        im = drawBoundingBox(im, boundingBox)
    imCentered = centerImage(im, boundingBox)
    # draw crosshairs
    if config.drawCrosshairs:
        imCentered[399, 0:799] = 0.25
        imCentered[0:799, 399] = 0.25
    misc.imsave(outfile, imCentered)
    return True
    

def centerImage(im, boundingBox):
    "center image on bounding box, crop to it, return new image"
    
    # cx, cy = findCenterByBlob(im)
    # cx, cy = findCenterBy_edges(im)
    # x1,x2,y1,y2 = find_object_edges(im)
    [x1,y1,x2,y2] = boundingBox
    cx = (x1+x2)/2.0
    cy = (y1+y2)/2.0
    
    imwidth = im.shape[0]
    imheight = im.shape[1]
    
    # make a bigger canvas to place image im on
    newsize = (imwidth * 2, imheight * 2)
    canvas = np.zeros(newsize)
    
    # put image on canvas centered on bounding box
    # eg canvas[800-cx:1600-cx, 800-cy:1600-cy] = np.array(im)
    canvas[imwidth-cx : imwidth-cx+imwidth, imheight-cy : imheight-cy+imheight] = np.array(im)

    # crop canvas to original image size
    # eg imcrop = canvas[400:1200, 400:1200]
    imcrop = canvas[imwidth/2 : imwidth/2+imwidth, imheight/2 : imheight/2+imheight]
    
    return imcrop


def drawBoundingBox(im, boundingBox):
    "draw a box on image, return new image"
    
    [x1,y1,x2,y2] = boundingBox
    
    imBox = np.copy(im)
    
    c = 0.5
    imBox[x1:x2,y1] = c
    imBox[x1:x2,y2] = c 
    imBox[x1,y1:y2] = c
    imBox[x2,y1:y2] = c
    
    #. or this, but what is plt?
    # plt.gca().add_patch(patches.Rectangle((y1,x1), y2-y1, x2-x1, fill=False, edgecolor="green", linewidth=0.5))
    
    return imBox



def findBoundingBox(im):
    """find the center of a planet using blobs, hough circle detection, and/or other means,
    and return the bounding box"""
    boundingBox = findBoundingBoxByBlob(im)
    [x1,y1,x2,y2] = boundingBox
    width = x2 - x1
    height = y2 - y1
    if abs(width-height) > 10:
        x,y,r = findCircle(im)
        x1 = x-r
        x2 = x+r
        y1 = y-r
        y2 = y+r
        boundingBox = [x1,y1,x2,y2]
    return boundingBox
    

def findBoundingBoxByBlob(im):
    "Find the largest blob in the given image and return the bounding box [x1,y1,x2,y2]"
    
    # for blob detection
    import scipy.ndimage as ndimage # for measurements, find_objects

    def findBlobs(im):
        "Find set of blobs in the given image"
        # b = 1*(im>epsilon) # threshold to binary image
        b = 1*(im>config.blobEpsilon) # threshold to binary image
        lbl, nobjs = ndimage.measurements.label(b) # label objects
        # find position of objects - index is 0-based
        blobs = ndimage.find_objects(lbl)
        return blobs

    def findLargestBlob(blobs):
        "Find largest blob in the given array of blobs"
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

    blobs = findBlobs(im)
    if len(blobs)>0:
        # find largest object
        blob = findLargestBlob(blobs)
        # get bounding box
        x1 = blob[0].start
        x2 = blob[0].stop
        y1 = blob[1].start
        y2 = blob[1].stop
    else:
        # if no blobs just return the whole image
        x1 = 0
        x2 = im.shape[0] - 1
        y1 = 0
        y2 = im.shape[1] - 1

    #. sometimes get > 799
    if x2>=im.shape[0]:
        x2 = im.shape[0] - 1
    if y2>=im.shape[1]:
        y2 = im.shape[1] - 1
    boundingBox = [x1,y1,x2,y2]
    # print boundingBox
    return boundingBox




# def findCenterByBox(im, epsilon=0, N=5):
def findCenterByBox(im):
    "find edges of largest object in image based on the most prominent edges, and return bounding box"

    # def findEdges1d(a, epsilon = 0):
    def findEdges1d(array):
        "find edges>epsilon in 1d array from left and right directions, return first,last indexes"
        icount = len(array)
        istart = 4 #. why skip 4? oh, the running average of N=5 columns
        iend = icount # skip 4 here also?
        # epsilon is the threshold value over which the smoothed value must cross
        epsilon = config.boxEpsilon
        # find first value over threshold
        ifirst = 0
        for i in xrange(istart, iend, 1):
            if array[i] > epsilon:
                ifirst = i
                break
        # find last value over threshold
        ilast = iend-1
        for i in xrange(iend-1, istart-1, -1):
            if array[i] > epsilon:
                ilast = i
                break
        return ifirst,ilast

    # def findEdges(im, axis, epsilon=0, N=5):
    def findEdges(im, axis):
        "find the edges for the given axis (0 or 1), return min,max"
        sums = np.sum(im, axis=axis)
        diff = np.diff(sums)
        diffsq = np.square(diff)
        diffsqln = np.log(diffsq)
        # config.N is the number of rows/columns to average over, for running average
        N = config.box_N
        if N>0:
            smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
            i1, i2 = findEdges1d(smoothed)
        else:
            i1, i2 = findEdges1d(diffsqln)
        return i1, i2

    x1, x2 = findEdges(im, 1)
    y1, y2 = findEdges(im, 0)
    
    #. now try to make it a square
    
    boundingBox = [x1,y1,x2,y2]
    return boundingBox



# simple test

def test():
    
    # infile = 'test/test.png'
    infile = 'test/test2.png'
    
    # load image
    im = mpim.imread(infile)
    
    # find bounding box around planet
    # boundingBox = findBoundingBoxByBlob(im)
    # boundingBox = findCenterByBox(im)
    boundingBox = findBoundingBox(im)
    print boundingBox

    # draw bounding box, save image
    imBox = drawBoundingBox(im, bounding_box)
    misc.imsave('test/test_bounding_box.png', imBox)

    # center image, save image
    imCentered = centerImage(im, boundingBox)
    misc.imsave('test/test_centered.png', imCentered)

    # test the center_image_file fn
    centerImageFile('test/test.png', 'test/test_cif.png')
    
    print 'done.'
    
    
if __name__ == '__main__':
    test()


