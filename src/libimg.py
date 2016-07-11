
# image processing routines


import matplotlib.image as mpim # for imread
import scipy.misc as misc # for imsave
import scipy.ndimage as ndimage # n-dimensional images - for blob detection
import numpy as np # for zeros, array, copy
import cv2 # for hough circle detection


#. should pass any constants into functions
import config




def getBlobDetector(minThreshold=10, maxThreshold=20, thresholdStep=10):
    "get a cv2 simple blob detector"
    # details: http://docs.opencv.org/master/d0/d7a/classcv_1_1SimpleBlobDetector.html#gsc.tab=0
    # keypoint params: http://docs.opencv.org/2.4/modules/features2d/doc/common_interfaces_of_feature_detectors.html
    # sourcecode: https://github.com/opencv/opencv/blob/1307bb1d033af3baeb55afb63c3989d3d6791c80/modules/features2d/src/blobdetector.cpp
    
    # You should set filterBy* to true/false to turn on/off corresponding filtration. Available filtrations:
    # By color. This filter compares the intensity of a binary image at the
    # center of a blob to blobColor. If they differ, the blob is filtered out.
    # Use blobColor = 0 to extract dark blobs and blobColor = 255 to extract
    # light blobs.
    # Default values of parameters are tuned to extract dark circular blobs.
    # ie it's easier than subtracting entire array from 255
    
    params = cv2.SimpleBlobDetector_Params()
    # print params.thresholdStep # default=10.0
    # print params.minDistBetweenBlobs # default=10.0
    # print params.filterByArea # default=True
    # print params.maxArea # default=5000.0
    params.minThreshold = minThreshold;
    params.maxThreshold = maxThreshold;
    params.thresholdStep = thresholdStep;
    params.filterByColor = True
    params.blobColor = 255 # use 255 to extract light colored blobs
    # params.filterByArea = False
    params.filterByArea = True
    params.minArea = 1
    params.maxArea = 1000000 # ? 
    ver = (cv2.__version__).split('.')
    # print ver # [2,4,3]
    if int(ver[0]) < 3 :
        detector = cv2.SimpleBlobDetector(params)
    else : 
        detector = cv2.SimpleBlobDetector_create(params)
    return detector


def show(im):
    "Show a cv2 image and wait for a keypress"
    cv2.imshow("cv2 image - press escape to continue", im)
    cv2.waitKey(0)    


def showMpim(im):
    "Show an mpim image and wait for a keypress"
    im2 = mpim2cv2(im)
    show(im2)

    
def combineChannels(channels):
    "combine the given weighted channels and return a single image"
    
    # eg channels = {
    # 'Orange':'composites/orange.png',
    # 'Green':'composites/green.png',
    # 'Blue':'composites/blue.png',
    # }
    # if missing a channel will use a blank/black image for that channel
    
    # get filenames
    redfile = channels.get('Orange')
    greenfile = channels.get('Green') or channels.get('Clear')
    bluefile = channels.get('Blue') or channels.get('Violet') or channels.get('Ultraviolet')
    
    # read images
    # returns None if filename is invalid - doesn't throw an error
    red = cv2.imread(redfile,cv2.IMREAD_GRAYSCALE)
    green = cv2.imread(greenfile,cv2.IMREAD_GRAYSCALE)
    blue = cv2.imread(bluefile,cv2.IMREAD_GRAYSCALE)
    
    # assign a blank image if missing a channel
    blank = np.zeros((800,800), np.uint8)
    if red==None:
        red = blank
    if green==None:
        green = blank
    if blue==None:
        blue = blank
    
    # apply weights
    # blue = cv2.multiply(blue,0.6)
    # red = cv2.multiply(red,0.5)
    # green = cv2.multiply(green,1.0)

    # merge channels - BGR for cv2
    im = cv2.merge((blue, green, red))
    
    return im



def mpim2cv2(im):
    "convert mpim (matplotimage library) image to cv2 (opencv) image"
    # mpim images are 0.0-1.0, cv2 are 0-255
    # im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
    im = im.astype('uint8')
    # print type(im)
    # print im.shape
    # print type(im[0,0])
    return im

    # A simple call to the imread method loads our image as a multi-dimensional
    # NumPy array (one for each Red, Green, and Blue component, respectively)
    # im = mpim.imread(infile)
    # OpenCV represents RGB images as multi-dimensional NumPy arrays - but in reverse order!
    # This means that images are actually represented in BGR order rather than RGB!
    # im = cv2.imread(infile)
    # There's an easy fix though. All we need to do is convert the image from BGR to RGB
    # im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    
    # # output = im.copy()
    # # gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    # print type(gray)
    # print gray.shape
    # print type(gray[0,0])
    
    
    
def drawCircle(im, circle, color = (0,255,0)):
    "draw a (green) circle on the image"
    (x,y,r) = circle
    lineWidth = 1
    cv2.circle(im, (x,y), r, color, lineWidth)


def findBoundingBoxByCircle(im):
    "Find the bounding box enclosing the best circle in image and return it."
    circle = findCircle(im)
    # if circle!=None:
    if type(circle) != type(None):
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
    # if circles!=None:
    if type(circles) != type(None):
        circle = circles[0]
        return circle # (x,y,r)
    else:
        return None


def gray2rgb(im):
    "convert a gray cv2 image to rgb, return new image"
    im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
    return im


def findCircles(im):
    "find circles in the given grayscale image"
    # internally the HoughCircles function calls the Canny edge detector
    
    # convert mpim image to cv2 image format
    # ok if im is already cv2 format
    im = mpim2cv2(im)
    
    method = cv2.cv.CV_HOUGH_GRADIENT
    
    # size of parameter space relative to input image - should affect precision of result
    dp = 1 
    
    # distance between circles
    # minDist = 1 # way too many found
    # minDist = 10 
    minDist = 200
    # minDist = 1000
    
    # First method-specific parameter. In case of CV_HOUGH_GRADIENT,
    # it is the higher threshold of the two passed to the Canny() edge
    # detector (the lower one is twice smaller).
    # Param 1 will set the sensitivity; how strong the edges of the circles need
    # to be. Too high and it won't detect anything, too low and it will find too
    # much clutter.
    canny_threshold=200 # 0-255?
    
    # Second method-specific parameter. In case of CV_HOUGH_GRADIENT,
    # it is the accumulator threshold for the circle centers at the detection
    # stage. The smaller it is, the more false circles may be detected. Circles,
    # corresponding to the larger accumulator values, will be returned first.
    # Param 2 will set how many edge points it needs to find to
    # declare that it's found a circle. Again, too high will detect nothing, too
    # low will declare anything to be a circle. The ideal value of param 2 will
    # be related to the circumference of the circles.
    # acc_threshold=50
    # acc_threshold=200
    acc_threshold=250
    # acc_threshold=300
    # acc_threshold=500
    # acc_threshold=600
    # acc_threshold=750
    # acc_threshold=1000
    
    # not sure what units these are - need a min of 1 to find one with fairly large radius
    minRadius=1
    maxRadius=10
    
    circles = cv2.HoughCircles(im, method, dp, minDist, canny_threshold, acc_threshold, minRadius, maxRadius)
    # if circles is not None:
    if type(circles) != type(None):
        circles = circles[0,:] # extract array
        # circles = np.round(circles).astype('int') # round all values to ints
        return circles # array of (x,y,r)
    else:
        return None
    

#. remove param
def centerImageFile(infile, outfile, blobThreshold, rotateImage=False):
    "center the given image file on a planet"
    im = mpim.imread(infile)
    if rotateImage:
        im = np.rot90(im, 2) # rotate by 180
    if config.centerMethod=='blob':
        # boundingBox = findBoundingBoxByBlob(im, blobThreshold)
        boundingBox = findBoundingBoxByBlob2(im)
    elif config.centerMethod=='box':
        boundingBox = findBoundingBoxByEdges(im)
    elif config.centerMethod=='circle':
        boundingBox = findBoundingBoxByCircle(im)
    elif config.centerMethod=='all':
        boundingBox = findBoundingBox(im, blobThreshold)
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


#. remove param
def findBoundingBox(im, blobThreshold):
    """find the center of a planet using blobs, hough circle detection, and/or other means,
    and return the bounding box"""
    # boundingBox = findBoundingBoxByBlob(im, blobThreshold)
    boundingBox = findBoundingBoxByBlob2(im)
    [x1,y1,x2,y2] = boundingBox
    if config.drawBlob:
        im = drawBoundingBox(im, boundingBox)
    # make sure box is ~square
    width = x2 - x1
    height = y2 - y1
    if abs(width-height) > 10: #. arbitrary parameter
        # # make sure center of box would be on screen (hough doesn't work otherwise)
        # x = (x1+x2)/2
        # y = (y1+y2)/2
        # if x>=0 and x<800 and y>=0 and y<800:
        #     boundingBox = findBoundingBoxByCircle(im) # use hough to find circlce
        # boundingBox = findBoundingBoxByCircle(im) # use hough to find circlce
        # print boundingBox
        # imcrop = im[y1:y2,x1:x2]
        imcrop = im[x1:x2,y1:y2]
        # print imcrop
        if width!=0 and height!=0:
            boundingBox = findBoundingBoxByCircle(imcrop) # use hough to find circle
            boundingBox[0] += x1
            boundingBox[1] += y1
            boundingBox[2] += x1
            boundingBox[3] += y1
    return boundingBox


def findBoundingBoxByBlob2(im):
    "find the biggest and best blob, iterating over different threshold values. returns bounding box"
    #. clean up
    
    # calls findBoundingBoxByBlob ~15 times.
    # but seems able to handle many different lighting conditions.
    # the idea is to look for the place where the slope of area vs threshold starts to level out.
    # that seemed to be the tipping point of where to find the best threshold value.
    
    # iterate over threshold values
    # th is threshold
    thmin = 0.05
    thmax = 0.20
    thstep = 0.01
    imax = int((thmax-thmin)/thstep)+1

    lastarea = 1
    maxarea = 800*800.0
    maxderiv = 1/thstep  # ie going from area=1 to area=0 in the delta of thstep
    thdiff = -0.9 # this seemed to be a good point to look for the inflection, based on some matplotlib plots for various images
    thbest = 0
    areabest = 0
    boundingBoxBest = [0,0,799,799]
    for i in range(0,imax):
        th = thmin + i * thstep
        boundingBox = findBoundingBoxByBlob(im, th)
        x1,y1,x2,y2 = boundingBox
        area = (x2-x1)*(y2-y1) / maxarea # area = 0 to 1
        deriv = (area - lastarea) / thstep / maxderiv
        if deriv>thdiff:
            thbest = th
            areabest = area
            boundingBoxBest = boundingBox
        lastarea = area
    return boundingBoxBest



def findBoundingBoxByBlob(im, blobThreshold):
    "Find the largest blob in the given image and return the bounding box [x1,y1,x2,y2]"
    
    def findBlobs(im):
        "Find set of blobs in the given image"
        b = 1*(im>blobThreshold) # threshold to binary image
        # b = 1*(im>config.blobEpsilon) # threshold to binary image
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

    #. sometimes get > 799 ? 
    if x2>=im.shape[0]:
        x2 = im.shape[0] - 1
    if y2>=im.shape[1]:
        y2 = im.shape[1] - 1
        
    boundingBox = [x1,y1,x2,y2]
    return boundingBox



# # def findBoundingBoxByEdges(im, epsilon=0, N=5):
# def findBoundingBoxByEdges(im):
#     "find edges of largest object in image based on the most prominent edges, and return bounding box"

#     # def findEdges1d(a, epsilon = 0):
#     def findEdges1d(array):
#         "find edges>epsilon in 1d array from left and right directions, return first,last indexes"
#         icount = len(array)
#         istart = 4 #. why skip 4? oh, the running average of N=5 columns
#         iend = icount # skip 4 here also?
#         # epsilon is the threshold value over which the smoothed value must cross
#         epsilon = config.boxEpsilon
#         # find first value over threshold
#         ifirst = 0
#         for i in xrange(istart, iend, 1):
#             if array[i] > epsilon:
#                 ifirst = i
#                 break
#         # find last value over threshold
#         ilast = iend-1
#         for i in xrange(iend-1, istart-1, -1):
#             if array[i] > epsilon:
#                 ilast = i
#                 break
#         return ifirst,ilast

#     # def findEdges(im, axis, epsilon=0, N=5):
#     def findEdges(im, axis):
#         "find the edges for the given axis (0 or 1), return min,max"
#         sums = np.sum(im, axis=axis)
#         diff = np.diff(sums)
#         diffsq = np.square(diff)
#         diffsqln = np.log(diffsq)
#         # config.N is the number of rows/columns to average over, for running average
#         N = config.boxN
#         if N>0:
#             smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
#             i1, i2 = findEdges1d(smoothed)
#         else:
#             i1, i2 = findEdges1d(diffsqln)
#         return i1, i2

#     x1, x2 = findEdges(im, 1)
#     y1, y2 = findEdges(im, 0)
    
#     #. now try to make it a square
    
#     boundingBox = [x1,y1,x2,y2]
#     return boundingBox



def test():
    print 'start'
    
    # infile = 'test/test.png'  # simple view
    # infile = 'test/test2.png'  # gap in planet
    infile = 'test/test3.png'  # limb at edge of image; center offscreen
    
    # load image
    im = mpim.imread(infile)

    # rotate image
    im = np.rot90(im, 2) # rotate by 180
    
    # # find circle
    # circle = findCircle(im)
    # print circle
    # drawCircle(im, circle)
    # misc.imsave('test/test_circle.png', im)
    
    # find bounding box around planet
    # boundingBox = findBoundingBoxByBlob(im)
    # boundingBox = findBoundingBoxByEdges(im)
    boundingBox = findBoundingBoxByCircle(im)
    # boundingBox = findBoundingBox(im)
    print boundingBox

    # draw bounding box
    im = drawBoundingBox(im, boundingBox)
    
    # save image
    # misc.imsave('test/test_bounding_box.png', im)

    # center image
    im = centerImage(im, boundingBox)
    
    # draw crosshairs
    im[399, 0:799] = 0.25
    im[0:799, 399] = 0.25
    
    # save image
    # misc.imsave('test/test_centered.png', im)

    # test the center_image_file fn
    # centerImageFile(infile, 'test/test_cif.png')
    # centerImageFile(infile, 'test/test_cif.png', True)

    print 'done.'
    
    
if __name__ == '__main__':
    test()


