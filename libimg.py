
# image processing routines


import matplotlib.image as mpim # for imread
import scipy.misc as misc # for imsave
import scipy.ndimage as ndimage # n-dimensional images - for blob detection
import numpy as np # for zeros, array, copy
import cv2 # for hough circle detection


#. cheating for now
import config



def mpim2cv2(im):
    "convert mpim image to cv2 image"
    # im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
    im = im.astype('uint8')
    # print type(im)
    # print im.shape
    # print type(im[0,0])
    # cv2.imshow("image",im)
    # cv2.waitKey(0)
    return im

    # A simple call to the imread method loads our image as a multi-dimensional
    # NumPy array (one for each Red, Green, and Blue component, respectively)
    # im = mpim.imread(infile)
    # OpenCV represents RGB images as multi-dimensional NumPy arrays - but in reverse order!
    # This means that images are actually represented in BGR order rather than RGB!
    # im = cv2.imread(infile)
    # There's an easy fix though.
    # All we need to do is convert the image from BGR to RGB
    # im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    
    # # output = im.copy()
    # # gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    # print type(gray)
    # print gray.shape
    # print type(gray[0,0])
    
    # gray = im.copy()
    # rotate 180deg
    # rows, cols = gray.shape
    # M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
    # gray = cv2.warpAffine(gray, M, (cols, rows))
    

    
    
def drawCircle(im, circle):
    ""
    # cv2.circle(im, (x,y), r, (0,255,0), 4)
    im = im.copy()
    (x,y,r) = circle
    cv2.circle(im, (x,y), r, (0,255,0), 2)
    return im
    


def findBoundingBoxByCircle(im):
    "Find the bounding box enclosing the best circle in image and return it."
    circle = findCircle(im)
    if circle!=None:
        (x,y,r) = circle        
        #. note: x and y are reversed (rows given first?)
        x1 = y-r
        x2 = y+r
        y1 = x-r
        y2 = x+r
    else:
        # if no circles just return the whole image
        x1 = 0
        x2 = im.shape[0] - 1
        y1 = 0
        y2 = im.shape[1] - 1
    boundingBox = [x1,y1,x2,y2]
    return boundingBox


def findCircle(im):
    "find best(?) circle in given image/file"
    circles = findCircles(im)
    if circles!=None:
        circle = circles[0]
        return circle # (x,y,r)
    else:
        return None

    
def findCircles(im):
    "find circles in the given image/file"
    
    # convert mpim image to cv2 image format
    im = mpim2cv2(im)

    gray = im
    
    # param1  -  First method-specific parameter. In case of CV_HOUGH_GRADIENT
    # , it is the higher threshold of the two passed to the Canny() edge
    # detector (the lower one is twice smaller).
    
    # param2  -  Second method-specific parameter. In case of CV_HOUGH_GRADIENT
    # , it is the accumulator threshold for the circle centers at the detection
    # stage. The smaller it is, the more false circles may be detected. Circles,
    # corresponding to the larger accumulator values, will be returned first.
    
    # So, as you can see, internally the HoughCircles function calls the Canny
    # edge detector, this means that you can use a gray image in the function,
    # instead of their contours.

    dp = 1.2 # size of parameter space relative to input image
    minDist = 1000 # distance between circles
    # minDist = 1 # distance between circles
    param1=0.1
    param2=200
    minRadius=10
    maxRadius=100
    circles = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT,
                               dp, minDist, param1, param2, minRadius, maxRadius)
    if circles is not None:
        circles = np.round(circles[0,:]).astype('int')
        return circles # array of (x,y,r)
    else:
        return None
    


def centerImageFile(infile, outfile, rotateImage=False):
    "center the given image file on a planet"
    im = mpim.imread(infile)
    if rotateImage:
        im = np.rot90(im, 2) # rotate by 180
    if config.centerMethod=='blob':
        boundingBox = findBoundingBoxByBlob(im)
    elif config.centerMethod=='box':
        boundingBox = findBoundingBoxByEdges(im)
    elif config.centerMethod=='circle':
        boundingBox = findBoundingBoxByCircle(im)
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
    
    # cx, cy = findBoundingBoxByBlob(im)
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
    
    cv2.rectangle(imBox, (y1,x1), (y2,x2), (0,255,0), 2)
    
    # c = 0.5
    # imBox[x1:x2,y1] = c
    # imBox[x1:x2,y2] = c 
    # imBox[x1,y1:y2] = c
    # imBox[x2,y1:y2] = c
    
    # but this can go out of bounds
    # imBox[x1+1:x2+1,y1+1] = c
    # imBox[x1+1:x2+1,y2+1] = c 
    # imBox[x1+1,y1+1:y2+1] = c
    # imBox[x2+1,y1+1:y2+1] = c
    
    # or this
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
        boundingBox = findBoundingBoxByCircle(im)
    return boundingBox
    

def findBoundingBoxByBlob(im):
    "Find the largest blob in the given image and return the bounding box [x1,y1,x2,y2]"
    
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
    return boundingBox



# def findBoundingBoxByEdges(im, epsilon=0, N=5):
def findBoundingBoxByEdges(im):
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
        N = config.boxN
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



def test():
    print 'start'
    
    # infile = 'test/test.png'  # simple view
    infile = 'test/test2.png'  # gap in planet
    
    # load image
    im = mpim.imread(infile)

    # rotate image
    im = np.rot90(im, 2) # rotate by 180
    
    # find circle
    circle = findCircle(im)
    print circle
    im = drawCircle(im, circle)
    misc.imsave('test/test_circle.png', im)
    
    # find bounding box around planet
    # boundingBox = findBoundingBoxByBlob(im)
    # boundingBox = findBoundingBoxByEdges(im)
    boundingBox = findBoundingBoxByCircle(im)
    # boundingBox = findBoundingBox(im)
    print boundingBox

    # draw bounding box
    im = drawBoundingBox(im, boundingBox)
    
    # save image
    misc.imsave('test/test_bounding_box.png', im)

    # center image
    im = centerImage(im, boundingBox)
    
    # draw crosshairs
    im[399, 0:799] = 0.25
    im[0:799, 399] = 0.25
    
    # save image
    misc.imsave('test/test_centered.png', im)

    # test the center_image_file fn
    # centerImageFile(infile, 'test/test_cif.png')
    centerImageFile(infile, 'test/test_cif.png', True)

    print 'done.'
    
    
if __name__ == '__main__':
    test()


