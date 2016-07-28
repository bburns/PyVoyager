
# image processing routines
# some are generic, some specific to PyVoyager


import os
import matplotlib.image as mpim # for imread, imsave
import scipy.ndimage as ndimage # n-dimensional images - for blob detection
import scipy.misc as misc # for imsave - uses PIL - see http://stackoverflow.com/a/1713101/243392
import numpy as np # for zeros, array, copy
import cv2 # for hough circle detection
import math # for log
import random


#. should pass any constants into functions
import config





def centerAndStabilizeImageFile(infile, outfile, fixedfile, lastRadius):
    "center an image file on target, then stabilize it relative to the given fixed file"
    #. this logic is pretty complicated - simplify
    x,y,radius = centerImageFile(infile, outfile)
    stabilizationOk = True
    # if given a fixedfile also, and radius not too different, try to stabilize against that
    if fixedfile and abs(radius-lastRadius)<20:
        im1 = cv2.imread(fixedfile)
        im2 = cv2.imread(outfile)
        im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
        sz = im1.shape
        warp_mode = cv2.MOTION_TRANSLATION
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        number_of_iterations = 5000
        termination_eps = 1e-10
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                    number_of_iterations,  termination_eps)
        # run the ECC algorithm - the results are stored in warp_matrix
        # throws an error if doesn't converge, so catch it
        try:
            cc, warp_matrix = cv2.findTransformECC (im1_gray, im2_gray, warp_matrix,
                                                    warp_mode, criteria)
        except:
            # if can't find solution, images aren't close enough in similarity
            stabilizationOk = False
        else:
            # print warp_matrix
            # [[ 1.          0.          1.37005 ]
            #  [ 0.          1.          0.485788]]
            # note: x and y are reversed!
            deltay = warp_matrix[0][2]
            deltax = warp_matrix[1][2]
            eps = 18 #. another parameter
            if abs(deltax) > eps or abs(deltay) > eps:
                stabilizationOk = False
            else:
                im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]),
                                             flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
                cv2.imwrite(outfile, im2_aligned)
                x += int(deltax)
                y += int(deltay)
    return x,y,radius,stabilizationOk



def centerImageFile(infile, outfile, debugtitle=None):
    "Center the given image file on a target and save it to outfile."
    # returns x,y,radius

    im = mpim.imread(infile)

    boundingBox = [0,0,799,799]

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

    # this actually does min/max optimization - see http://stackoverflow.com/a/1713101/243392
    # but the CALIB images are really dark, and this result looks nice, so leaving it for now
    misc.imsave(outfile, im)

    # return boundingBox

    # return center
    x = int((boundingBox[0] + boundingBox[2])/2)
    y = int((boundingBox[1] + boundingBox[3])/2)
    # return x, y
    #. this is cheating, but it works so far
    radius = int((boundingBox[2]-x + boundingBox[3]-y)/2)
    return x, y, radius


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


def adjustImageFile(infile, outfile, debugtitle=None):
    "Adjust the given image file and save it to outfile - stretch histogram and rotate 180deg."
    #. could subtract dark current image, remove reseau marks if starting from RAW images, etc

    im = mpim.imread(infile)

    # adjust image
    im = np.rot90(im, 2) # rotate by 180

    # this actually saves bw images with a colormap
    # mpim.imsave(outfile, im)

    # this actually does min/max optimization - see http://stackoverflow.com/a/1713101/243392
    # the CALIB images are really dark, and this result looks nice
    misc.imsave(outfile, im)


def translateImageFile(infile, outfile, x, y):
    "center an image file on x,y"
    im = mpim.imread(infile)
    boundingBox = [x,y,x,y]
    im = centerImage(im, boundingBox)
    if config.drawCrosshairs:
        im[399, 0:799] = 0.25
        im[0:799, 399] = 0.25
    # this actually saves bw images with a colormap
    # mpim.imsave(outfile, im)
    # this actually does min/max optimization - see http://stackoverflow.com/a/1713101/243392
    # but the CALIB images are really dark, and this result looks nice, so leaving it for now
    misc.imsave(outfile, im)






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

    # if just one channel then return a bw image
    if len(channels)==1:
        filename = channels.values()[0]
        gray = cv2.imread(filename,cv2.IMREAD_GRAYSCALE)
        return gray

    # get filenames
    #. what are ch4_js and ch4_u ?
    redfilename = channels.get('Orange') or channels.get('Clear')
    greenfilename = channels.get('Green') or channels.get('Clear')
    bluefilename = channels.get('Blue') or channels.get('Violet') or channels.get('Uv') or \
                   channels.get('Ch4_Js') or channels.get('Ch4_U') or channels.get('Clear')

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
    # plt.gca().add_patch(patches.Rectangle((y1,x1), y2-y1, x2-x1, fill=False,
    #                     edgecolor="green", linewidth=0.5))

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

    # Hough detection parameters

    # only available method now
    # method = cv2.cv.CV_HOUGH_GRADIENT
    method = cv2.HOUGH_GRADIENT # if get error value not found, upgrade to cv2 v3

    # size of parameter space relative to input image - should affect precision of result
    # dp = 1
    # dp = 2 # didn't seem to help with jitters
    dp = config.houghParameterSpace

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
    canny_threshold = config.cannyUpperThreshold # eg 200

    # Second method-specific parameter. In case of CV_HOUGH_GRADIENT,
    # it is the accumulator threshold for the circle centers at the detection
    # stage. The smaller it is, the more false circles may be detected. Circles,
    # corresponding to the larger accumulator values, will be returned first.
    # Param 2 will set how many edge points it needs to find to
    # declare that it's found a circle. Again, too high will detect nothing, too
    # low will declare anything to be a circle. The ideal value of param 2 will
    # be related to the circumference of the circles. [?]
    acc_threshold = config.houghAccumulatorThreshold
    # acc_threshold=50
    # acc_threshold=200
    # acc_threshold=250
    # acc_threshold=300
    # acc_threshold=500
    # acc_threshold=600
    # acc_threshold=750
    # acc_threshold=1000

    # not sure what units these are - need a min of 1 to find one with fairly large radius
    # minRadius=1
    # maxRadius=10
    minRadius = config.houghMinRadius
    maxRadius = config.houghMaxRadius

    circles = cv2.HoughCircles(im, method, dp, minDist, canny_threshold,
                               acc_threshold, minRadius, maxRadius)

    if config.drawEdges:
        upper = config.cannyUpperThreshold
        lower = upper / 2
        imedges = cv2.Canny(im, lower, upper)
        cv2.imwrite(debugtitle + '_cannyedges.jpg', imedges)

    # if circles: # nowork in python
    if type(circles) != type(None):
        circles = circles[0,:] # extract array
        circle = circles[0]
        circle = np.round(circle).astype('int') # round all values to ints
        if config.drawCircle:
            im = gray2rgb(im)
            for circ in circles:
                circ = np.round(circ).astype('int')
                drawCircle(im, circ, (0,0,255)) # red
            drawCircle(im, circle) # green
            # show(im)
            # im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
            cv2.imwrite(debugtitle + '_circles.jpg', im)
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
        cv2.imwrite(debugtitle + '_binaryimage.jpg', b)

    # find position of objects - index is 0-based
    # http://docs.scipy.org/doc/scipy-0.16.1/reference/generated/scipy.ndimage.measurements.find_objects.html
    # http://stackoverflow.com/questions/22103572/how-to-find-the-rectangles-in-an-image
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
            if area>areamax:
                # check for min width and height so don't pick up edge artifacts
                if width>1 and height>1:
                    areamax = area
                    largestblob = blob
        # get bounding box
        if largestblob:
            x1 = largestblob[0].start
            x2 = largestblob[0].stop
            y1 = largestblob[1].start
            y2 = largestblob[1].stop

    boundingBox = [x1,y1,x2,y2]

    if config.drawBoundingBox:
        # drawBoundingBox(im, boundingBox)
        imbox = drawBoundingBox(im, boundingBox)
        imbox = cv2.normalize(imbox, None, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(debugtitle + '_blobboundingbox.jpg', imbox)
        # show(imbox)

    return boundingBox


# def findBoundingBox(im):
def findBoundingBox(im, debugtitle=None):
    "find bounding box returns [x1,y1,x2,y2]"
    # if debugtitle: print 'find bounding box for', debugtitle
    # looks for a small blob, then a large hough circle
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



def drawMatches(img1, kp1, img2, kp2, matches):
    # source: http://stackoverflow.com/questions/11114349/how-to-visualize-descriptor-matching-using-opencv-module-in-python
    """
    My own implementation of cv2.drawMatches as OpenCV 2.4.9
    does not have this function available but it's supported in
    OpenCV 3.0.0

    This function takes in two images with their associated
    keypoints, as well as a list of DMatch data structure (matches)
    that contains which keypoints matched in which images.

    An image will be produced where a montage is shown with
    the first image followed by the second image beside it.

    Keypoints are delineated with circles, while lines are connected
    between matching keypoints.

    img1,img2 - Grayscale images
    kp1,kp2 - Detected list of keypoints through any of the OpenCV keypoint
              detection algorithms
    matches - A list of matches of corresponding keypoints through any
              OpenCV keypoint matching algorithm
    """

    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')

    # Place the first image to the left
    out[:rows1,:cols1,:] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    out[:rows2,cols1:cols1+cols2,:] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:

        # Get the matching keypoints for each of the images
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        r = random.randint(100,255)
        g = random.randint(100,255)
        b = random.randint(100,255)
        color = (b,g,r)

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        # cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0), 1)
        # cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0), 1)
        cv2.circle(out, (int(x1),int(y1)), 4, color, 1)
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, color, 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        # cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0), 1)
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), color, 1)


    # Show the image
    cv2.imshow('Matched Features', out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

