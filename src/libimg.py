
# image processing routines
# some are generic, some specific to PyVoyager


import os
import matplotlib.image as mpim # for imread, imsave
import scipy.ndimage as ndimage # n-dimensional images - for blob detection
import scipy.misc as misc # for imsave - uses PIL - see http://stackoverflow.com/a/1713101/243392
import numpy as np # for zeros, array, copy
import cv2 # for hough circle detection
import math # for log


#. should pass any constants into functions
import config



def img2png(srcdir, filespec, destdir, img2pngOptions):
    "Convert all IMG files matching filespec in srcdir to PNG files in destdir"
    
    # first convert img's to png's, then move them to the dest dir
    savedir = os.getcwd()
    os.chdir(srcdir)
    # eg "img2png *CALIB.img -fnamefilter > nul"
    cmd = "img2png " + filespec + " " + img2pngOptions + " > nul"
    # print cmd
    os.system(cmd)
    
    # now move the png files to destdir
    # (srcdir is relative to the python program so need to switch back to that dir)
    os.chdir(savedir)
    # cmd = "mv " + srcdir +"*.png " + destdir + " > nul" # nowork on windows due to backslashes in srcdir
    cmd = "move " + srcdir +"\\*.png " + destdir + " > nul"
    # print cmd
    os.system(cmd)
    

# def centerImageFile(infile, outfile):
# def adjustImageFile(infile, outfile, docenter=True):
def adjustImageFile(infile, outfile, docenter=True, debugtitle=None):
    "Adjust and optionally center the given image file on a target and save it to outfile."
    # if docenter True, do everything but the centering step
    
    im = mpim.imread(infile)
    
    # adjust image
    # could subtract dark current image, remove reseau marks if starting from RAW images
    # or have that as a separate adjustments step
    im = np.rot90(im, 2) # rotate by 180
    
    boundingBox = [0,0,799,799]
    
    if docenter:
        # find the bounding box of biggest object
        # boundingBox = findBoundingBox(im)
        boundingBox = findBoundingBox(im, debugtitle)

        # center the image on the target
        im = centerImage(im, boundingBox)
    
        if config.drawCrosshairs:
            im[399, 0:799] = 0.25
            im[0:799, 399] = 0.25
        
    # this actually saves bw images with a colormap
    # mpim.imsave(outfile, im)
    
    # and this actually does min/max optimization - see http://stackoverflow.com/a/1713101/243392
    # but the CALIB images are really dark, and this result looks nice, so leaving it for now
    misc.imsave(outfile, im)
    
    return boundingBox
    

def show(im2, title='cv2 image - press esc to continue'):
    "Show a cv2 image and wait for a keypress"
    cv2.imshow(title, im2)
    cv2.waitKey(0)    


def showMpim(im, title='mpim image - press esc to continue'):
    "Show an mpim image and wait for a keypress"
    im2 = mpim2cv2(im)
    show(im2, title)

    
def combineChannels(channels):
    "combine the given weighted channel files and return a single cv2 image"
    #. could pass in weights, or just define them in config
    # eg channels = {
    #   'Orange':'composites/orange.png',
    #   'Green':'composites/green.png',
    #   'Blue':'composites/blue.png',
    # }
    # if missing a channel will use a blank/black image for that channel
    
    # get filenames
    #. what are ch4_js and ch4_u ? 
    redfilename = channels.get('Orange') or channels.get('Clear')
    greenfilename = channels.get('Green') or channels.get('Clear')
    bluefilename = channels.get('Blue') or channels.get('Violet') or channels.get('Uv') or channels.get('Ch4_Js') or channels.get('Ch4_U') or channels.get('Clear')
    
    # read images
    # returns None if filename is invalid - doesn't throw an error
    # (note: can't say 'or blank' here as in javascript)
    red = cv2.imread(redfilename,cv2.IMREAD_GRAYSCALE)
    green = cv2.imread(greenfilename,cv2.IMREAD_GRAYSCALE)
    blue = cv2.imread(bluefilename,cv2.IMREAD_GRAYSCALE)
    
    # assign a blank image if missing a channel
    blank = np.zeros((800,800), np.uint8)
    if type(red)==type(None): red = blank
    if type(green)==type(None): green = blank
    if type(blue)==type(None): blue = blank
    
    # apply weights
    # blue = cv2.multiply(blue,0.6)
    # red = cv2.multiply(red,0.5)
    # green = cv2.multiply(green,1.0)

    # merge channels - BGR for cv2
    im2 = cv2.merge((blue, green, red))
    
    return im2


def mpim2cv2(im):
    "Convert mpim (matplotimage library) image to cv2 (opencv) image."
    # mpim images are 0.0-1.0, cv2 are 0-255
    im2 = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
    im2 = im2.astype('uint8')
    return im2

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
    
    
def drawCircle(im2, circle, color = (0,255,0)):
    "Draw a circle on the given cv2 image."
    (x,y,r) = circle
    lineWidth = 1
    cv2.circle(im2, (x,y), r, color, lineWidth)


def gray2rgb(im2):
    "convert a gray cv2 image to rgb, return new image"
    im2 = cv2.cvtColor(im2, cv2.COLOR_GRAY2RGB)
    return im2


def drawBoundingBox(im, boundingBox):
    "draw a box on image"
    
    [x1,y1,x2,y2] = boundingBox
    imbox = np.copy(im)
    imbox = cv2.cvtColor(imbox, cv2.COLOR_GRAY2RGB)
    cv2.rectangle(imbox, (y1,x1), (y2,x2), (255,0,0), 2)
    return imbox

    # cv2.rectangle(im, (y1,x1), (y2,x2), (0,255,0), 2)
    
    # im = im.copy() # rect gives error otherwise
    # cv2.rectangle(im, (y1,x1), (y2,x2), 1)
    
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
    
    # return imBox

    
# def findCircle(im):
def findCircle(im, debugtitle=None):
    "Find best circle in given image, return as (x,y,r)"

    # internally the HoughCircles function calls the Canny edge detector
    
    # convert mpim image to cv2 image format - ok if im is already cv2 format
    im = mpim2cv2(im)

    # # don't modify the user's image
    # im = im.copy()
    # # stretch
    # # made it much worse
    # # im = cv2.normalize(im, None, 0, 1.0, cv2.NORM_MINMAX)
    # # get canny edges
    # # hough is supposed to do this but doesn't seem to work too well?
    # upper = 200
    # lower = upper/2
    # im = cv2.Canny(im, lower, upper)
    # # dilate the edges
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2))
    # im = cv2.dilate(im, kernel, iterations = 1)
    # # im = cv2.dilate(im, 2)
    
    # maybe add a sharpening step for blurry limbs? 
    # tested it on a blurry/dim jupiter image but didn't help canny edges at all
    
    # # blur image to diminish reseau marks
    # #. make this optional by param, or do as separate step
    # kernelSize = 5 # aperture size - should be odd
    # gaussianSigma = 7
    # im = cv2.GaussianBlur(im, (kernelSize, kernelSize), gaussianSigma)
    # if config.debugImages: show(im, 'findcircles - gaussian blurred')

    # Hough detection parameters
    
    # only available method now
    method = cv2.cv.CV_HOUGH_GRADIENT 
    
    # size of parameter space relative to input image - should affect precision of result
    dp = 1 
    # dp = 2 # didn't seem to help with jitters
    
    # distance between circles
    # minDist = 1 # way too many found
    # minDist = 10 # too many
    minDist = 200
    # minDist = 1000
    
    # First method-specific parameter. In case of CV_HOUGH_GRADIENT,
    # it is the higher threshold of the two passed to the Canny() edge
    # detector (the lower one is twice smaller).
    # Param 1 will set the sensitivity; how strong the edges of the circles need
    # to be. Too high and it won't detect anything, too low and it will find too
    # much clutter.
    # 0-255?
    canny_threshold=config.cannyUpperThreshold # eg 200
    
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

    if config.drawEdges:
        upper = config.cannyUpperThreshold
        lower = upper / 2
        imedges = cv2.Canny(im, lower, upper)
        cv2.imwrite(debugtitle + '_cannyedges.png', imedges)
    
    # if circles: # nowork in python
    if type(circles) != type(None):
        circles = circles[0,:] # extract array
        circle = circles[0]
        circle = np.round(circle).astype('int') # round all values to ints
        if config.drawCircle:
            im = gray2rgb(im)
            drawCircle(im, circle)
            # show(im)
            # im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
            cv2.imwrite(debugtitle + '_circles.png', im)
    else:
        circle = None
    return circle

    
def centerImage(im, boundingBox):
    "center image on bounding box, crop to it, return new image"
    
    [x1,y1,x2,y2] = boundingBox
    cx = int((x1+x2)/2.0)
    cy = int((y1+y2)/2.0)
    
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
    x1 = int(imwidth/2)
    y1 = int(imheight/2)
    imcrop = canvas[x1:x1+imwidth, y1:y1+imheight]
    
    return imcrop


# def findBoundingBoxByCircle(im):
def findBoundingBoxByCircle(im, debugtitle=None):
    "Find the bounding box enclosing the best circle in image and return it."
    # circle = findCircle(im)
    circle = findCircle(im, debugtitle)
    if type(circle) != type(None):
        # note: x and y are reversed (rows given first)
        (x,y,r) = circle        
        x1 = y-r
        x2 = y+r
        y1 = x-r
        y2 = x+r
        # if config.drawCircle:
        #     im = gray2rgb(im)
        #     drawCircle(im, circle)
        #     show(im)
    else:
        # if no circles just return the whole image
        x1 = 0
        x2 = im.shape[1] - 1
        y1 = 0
        y2 = im.shape[0] - 1
    boundingBox = [x1,y1,x2,y2]
    return boundingBox


# def findBoundingBoxByBlob(im, blobThreshold):
def findBoundingBoxByBlob(im, blobThreshold, debugtitle):
    "Find the largest blob in the given image and return the bounding box [x1,y1,x2,y2]"
    
    # threshold to binary image
    b = 1*(im>blobThreshold)
    
    # find and label blob objects
    labels, nobjs = ndimage.measurements.label(b) 
    
    if config.drawBinaryImage:
        b = cv2.normalize(b, None, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(debugtitle + '_binaryimage.png', b)
        
    # find position of objects - index is 0-based
    blobs = ndimage.find_objects(labels)
    
    # by default, if no blobs just return the whole image
    x1 = 0
    x2 = im.shape[1] - 1
    y1 = 0
    y2 = im.shape[0] - 1
    
    # find largest object, if any
    if len(blobs)>0:
        areamax = 0
        largestblob = None
        for blob in blobs:
            width = blob[0].stop - blob[0].start
            height = blob[1].stop - blob[1].start
            area = width * height
            # check for min width and height so don't pick up edge artifacts
            if area>areamax and width>1 and height>1:
                areamax = area
                largestblob = blob
        # get bounding box
        if largestblob:
            x1 = largestblob[0].start
            x2 = largestblob[0].stop
            y1 = largestblob[1].start
            y2 = largestblob[1].stop
        
    boundingBox = [x1,y1,x2,y2]

    # if config.debugImages:
    #     # b *= 255
    #     b = mpim2cv2(b)
    #     b = gray2rgb(b)
    #     drawBoundingBox(b, boundingBox)
    #     show(b, 'findblobs th=' + str(blobThreshold))
    
    if config.drawBoundingBox:
        # drawBoundingBox(im, boundingBox)
        imbox = drawBoundingBox(im, boundingBox)
        imbox = cv2.normalize(imbox, None, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(debugtitle + '_blobboundingbox.png', imbox)
        # show(imbox)
        
        
    return boundingBox


# def findBoundingBox(im):
def findBoundingBox(im, debugtitle=None):
    "find bounding box returns [x1,y1,x2,y2]"
    # if debugtitle: print 'find bounding box for', debugtitle
    # looks for a small blob, then a large hough circle
    #. do a pre-canny step? 
    # upper = 200
    # lower = 100
    # im = cv2.Canny(im, lower, upper)
    # boundingBox = findBoundingBoxByBlob(im, config.blobThreshold)
    boundingBox = findBoundingBoxByBlob(im, config.blobThreshold, debugtitle)
    [x1,y1,x2,y2] = boundingBox
    # if box is > some size, try looking for a circle
    width = x2 - x1
    height = y2 - y1
    area = width*height
    # if debugtitle: print 'area',area
    if area>config.blobAreaCutoff: # eg 10*10 pixels
        # boundingBox = findBoundingBoxByCircle(im) # use hough to find circle
        boundingBox = findBoundingBoxByCircle(im, debugtitle) # use hough to find circle
    return boundingBox



    
# if __name__ == '__main__':
#     pass

