
"""
Image processing routines

not reusable - many are specific to PyVoyager
"""

import os
import matplotlib.image as mpim # for imread, imsave
import scipy.ndimage as ndimage # n-dimensional images - for blob detection
import scipy.misc as misc # for imsave - uses PIL - see http://stackoverflow.com/a/1713101/243392
import numpy as np # for zeros, array, copy
import cv2 # for hough circle detection
import math # for log
import random


import config



def resizeImage(im, w, h):
    "Resize image, keeping aspect ratio, filling in gaps with black, return new image."

    oldH, oldW = im.shape[:2]
    # print oldH, oldW
    aspectRatio = float(oldW) / float(oldH)
    # print aspectRatio
    if aspectRatio > 1: # width>height
        newW = w
        newH = int(newW / aspectRatio)
    else:
        newH = h
        newW = int(newH * aspectRatio)
    # print newH, newW
    im = cv2.resize(im, (newW,newH), interpolation=cv2.INTER_AREA)

    # add the new image to a blank canvas
    canvas = np.zeros((h,w,3), np.uint8)
    x = int((w-newW)/2)
    y = int((h-newH)/2)
    canvas[y:y+newH, x:x+newW] = np.array(im)
    return canvas



def stabilizeImageFile(infile, outfile, fixedfile, lastRadius, x,y,radius):
    """
    stabilize infile against fixedfile and write to outfile.

    #. rename these
    lastRadius is the radius of the target in the fixedfile,
    radius is the radius of the infile
    """
    # if no file to stabilize to, must be the first image in the sequence,
    # so just say it's stabilized
    if not fixedfile:
        stabilizationOk = True
    # if given a fixedfile try to stabilize against that
    else:
        stabilizationOk = False
        # this helps prevent stabilizing to badly centered images
        #. should be a percentage?
        if abs(radius-lastRadius)>config.stabilizeMaxRadiusDifference: # eg 20
            print
            print 'max radius delta exceeded', radius, lastRadius
        else:
            stabilizationOk = True
            im1 = cv2.imread(fixedfile)
            im2 = cv2.imread(outfile)
            im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
            im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
            sz = im1.shape
            warp_mode = cv2.MOTION_TRANSLATION
            warp_matrix = np.eye(2, 3, dtype=np.float32)
            number_of_iterations = config.stabilizeECCIterations
            termination_eps = config.stabilizeECCTerminationEpsilon
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
                # if image shifted too much, assume something went wrong
                if abs(deltax) > config.stabilizeMaxDeltaPosition or \
                   abs(deltay) > config.stabilizeMaxDeltaPosition:
                    print
                    print 'max delta position exceeded', deltax, deltay
                    stabilizationOk = False
                else:
                    im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]),
                                                 flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
                    cv2.imwrite(outfile, im2_aligned)
                    x += int(deltax)
                    y += int(deltay)
    # return x,y,radius,stabilizationOk
    return x,y,stabilizationOk


def centerImageFileAt(infile, outfile, x, y):
    """
    Center the given image file at the given x,y and save it to outfile.
    """
    im = mpim.imread(infile)
    # center the image on the target
    boundingBox = [x,y,x,y]
    im = centerImage(im, boundingBox)
    if config.drawCrosshairs:
        im[399, 0:799] = 0.25
        im[0:799, 399] = 0.25
    cv2.imwrite(outfile, im)


def centerImageFile(infile, outfile, radius=None):
    """
    Center the given image file on a target and save it to outfile.
    Returns x,y,radius
    """
    # im = mpim.imread(infile)
    # im = cv2.imread(infile)
    im = cv2.imread(infile, 0) #. param

    boundingBox = [0,0,799,799]

    # find the bounding box of biggest object
    # boundingBox = findBoundingBox(im)
    # boundingBox = findBoundingBox(im, debugtitle)
    # boundingBox = findBoundingBox(im, radius, debugtitle)
    boundingBox = findBoundingBox(im, radius)

    # center the image on the target
    im = centerImage(im, boundingBox)

    if config.drawCrosshairs:
        im[399, 0:799] = 0.25
        im[0:799, 399] = 0.25

    # this actually saves bw images with a colormap
    # mpim.imsave(outfile, im)

    # this actually does min/max optimization - see http://stackoverflow.com/a/1713101/243392
    # but the CALIB images are really dark, and this result looks nice, so leaving it for now
    # misc.imsave(outfile, im)
    #. this should be cv2.imwrite, as the adjust step already does this
    cv2.imwrite(outfile, im)

    x = int((boundingBox[0] + boundingBox[2])/2)
    y = int((boundingBox[1] + boundingBox[3])/2)
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
    #. use os.rename
    # (srcdir is relative to the python program so need to switch back to that dir)
    os.chdir(savedir)
    # cmd = "mv " + srcdir +"*.png " + destdir + " > nul" # nowork on windows due to backslashes
    cmd = "move " + srcdir +"\\*.png " + destdir + " > nul"
    # print cmd
    os.system(cmd)


# def adjustImageFile(infile, outfile, debugtitle=None):
def adjustImageFile(infile, outfile):
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


def show(im, title='cv2 image - press esc to continue'):
    "Show a cv2 image and wait for a keypress"
    cv2.imshow(title, im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def combineChannels(channels):
    """
    Combine the given channels and return a single cv2 image.

    If only one channel included will return a b/w image.
    If missing a channel will use a blank/black image for that channel.
    channels is an array of [filter, filename, <weight, x, y>]
    (the last 3 are optional)
    eg channels = [
      ['Orange','composites/orange.png'],
      ['Green','composites/green.png',0.8,30,40],
      ['Blue','composites/blue.png',0.9,50,66],
    ]
    """
    colFilter = 0
    colFilename = 1
    colWeight = 2
    colX = 4 # note: x and y are reversed, due to numpy's matrices being like matlab
    colY = 3
    colIm = -1

    # if just one channel then return a bw image
    if len(channels)==1:
        filename = channels[0][colFilename]
        gray = cv2.imread(filename,cv2.IMREAD_GRAYSCALE)
        return gray

    # find size of canvas that will contain all images
    xmin = 0; xmax = 799; ymin = 0; ymax = 799
    for row in channels:
        x = row[colX] if len(row)>colX else 0
        y = row[colY] if len(row)>colY else 0
        if x < xmin: xmin = x
        if x+799 > xmax: xmax = x+799
        if y < ymin: ymin = y
        if y+799 > ymax: ymax = y+799
    w = xmax-xmin+1; h = ymax-ymin+1
    enlarged = w!=800 or h!=800

    # get images for each channel
    rowRed = None
    rowGreen = None
    rowBlue = None
    for row in channels:
        filename = row[colFilename]
        # note: this returns None if filename is invalid - doesn't throw an error
        im = cv2.imread(filename,cv2.IMREAD_GRAYSCALE)
        # apply weight if necessary
        weight = row[colWeight] if len(row)>colWeight else 1.0
        if weight!=1.0: im = cv2.multiply(im,weight)
        # if canvas needs to be enlarged, do so
        if enlarged:
            canvas = np.zeros((w,h), np.uint8) # 0-255
            x = row[colX] if len(row)>colX else 0
            y = row[colY] if len(row)>colY else 0
            # print xmin,x,ymin,y
            # copy image into canvas at right point
            canvas[x-xmin:x-xmin+800, y-ymin:y-ymin+800] = np.array(im)
            im = canvas
        row.append(im)
        # now assign the row to one of the available channels
        # eventually would like something more accurate than just rgb
        filter = row[colFilter]
        if filter in ['Orange','Clear']:
            rowRed = row
        if filter in ['Green','Clear']:
            rowGreen = row
        if filter in ['Blue','Violet','Uv','Ch4_Js','Ch4_U','Clear']:
            rowBlue = row

    # assign a blank image if missing a channel
    blank = np.zeros((w,h), np.uint8)
    imRed = rowRed[colIm] if rowRed else blank
    imGreen = rowGreen[colIm] if rowGreen else blank
    imBlue = rowBlue[colIm] if rowBlue else blank

    # merge channels - BGR for cv2
    im = cv2.merge((imBlue, imGreen, imRed))

    # scale image to 800x800
    if enlarged:
        im = resizeImage(im, 800, 800)
        # im.thumbnail((800,800), Image.BICUBIC) # PIL

    # later - maybe crop canvas
    # eg im = im[400:1200, 400:1200]

    return im


def drawCircle(im, circle, color = (0,255,0)):
    """
    Draw a circle on the given cv2 image.
    circle is (x,y,radius), color is (b,g,r).
    """
    (x,y,r) = circle
    lineWidth = 1
    cv2.circle(im, (x,y), r, color, lineWidth)


def gray2rgb(im):
    "convert a gray cv2 image to rgb, return new image"
    im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
    return im


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


def findCircle(im, radius=None):
    "Find best circle in given image, with optional expected radius. Returns as (x,y,r)"
    # note: internally the HoughCircles function calls the Canny edge detector

    # convert mpim image to cv2 image format - ok if im is already cv2 format
    # im = mpim2cv2(im)

    # set Hough detection parameters

    # only available method now
    method = cv2.HOUGH_GRADIENT # if get error here, upgrade to cv2 v3

    # size of accumulator space relative to input image
    dp = config.houghAccumulatorSize

    # distance between circles
    # minDist = 1 # way too many found
    # minDist = 10 # too many
    minDist = 200

    # First method-specific parameter. In case of CV_HOUGH_GRADIENT,
    # it is the higher threshold of the two passed to the Canny() edge
    # detector (the lower one is twice smaller).
    # Param 1 will set the sensitivity; how strong the edges of the circles need
    # to be. Too high and it won't detect anything, too low and it will find too
    # much clutter.
    canny_threshold = config.houghCannyUpperThreshold # eg 200

    # Second method-specific parameter. In case of CV_HOUGH_GRADIENT,
    # it is the accumulator threshold for the circle centers at the detection
    # stage. The smaller it is, the more false circles may be detected. Circles,
    # corresponding to the larger accumulator values, will be returned first.
    # Param 2 will set how many edge points it needs to find to
    # declare that it's found a circle. Again, too high will detect nothing, too
    # low will declare anything to be a circle. The ideal value of param 2 will
    # be related to the circumference of the circles.
    # (so should be proportional to the radius)
    acc_threshold = config.houghAccumulatorThreshold

    if radius:
        pct = config.houghRadiusSearchPercent # eg 10
        minRadius = int((1-float(pct)/100)*radius)
        maxRadius = int((1+float(pct)/100)*radius)
    else:
        minRadius = 0
        maxRadius = 0

    circles = cv2.HoughCircles(im, method, dp, minDist,
                               param1 = canny_threshold,
                               param2 = acc_threshold,
                               minRadius = minRadius,
                               maxRadius = maxRadius)

    # draw canny edges
    if config.debugImageTitle:
        upper = config.houghCannyUpperThreshold
        lower = upper / 2
        imedges = cv2.Canny(im, lower, upper)
        cv2.imwrite(config.debugImageTitle + '_cannyedges.jpg', imedges)

    if circles is None:
        # print 'no circles found'
        circle = None
    else:
        circles = circles[0,:] # extract array
        circle = circles[0]
        circle = np.round(circle).astype('int') # round all values to ints
        # draw circles
        if config.debugImageTitle:
            im = gray2rgb(im)
            for circ in circles:
                circ = np.round(circ).astype('int')
                drawCircle(im, circ, (0,0,255)) # red
            drawCircle(im, circle) # green
            cv2.imwrite(config.debugImageTitle + '_circles.jpg', im)
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


def findBoundingBoxByCircle(im, radius):
    "Find the bounding box enclosing the best circle in image and return it."
    circle = findCircle(im, radius)
    if not circle is None:
        (x,y,r) = circle
        # note: x and y are reversed (rows given first)
        #. fix
        x1 = y-r
        x2 = y+r
        y1 = x-r
        y2 = x+r
        # x1 = x-r
        # x2 = x+r
        # y1 = y-r
        # y2 = y+r
    else:
        # if no circles just return the whole image
        x1 = 0
        x2 = im.shape[1] - 1
        y1 = 0
        y2 = im.shape[0] - 1
    boundingBox = [x1,y1,x2,y2]
    return boundingBox


def findBoundingBoxByBlob(im):
    "Find the largest blob in the given image and return the bounding box [x1,y1,x2,y2]"

    # threshold to binary image
    # b = 1*(im>blobThreshold)

    # adaptive thresholding -
    b = cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                              config.blobAdaptiveThresholdSize, # eg 9
                              config.blobAdaptiveThresholdConstant) # eg 6

    # find and label blob objects
    labels, nobjs = ndimage.measurements.label(b)

    # if config.drawBinaryImage:
    if config.debugImageTitle:
        cv2.imwrite(config.debugImageTitle + '_binaryimage.jpg', b)

    # find position of objects
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
                #. try larger and check if actually on edge
                # if width>2 and height>2:
                # if width>3 and height>3:
                    areamax = area
                    largestblob = blob
        # get bounding box
        if largestblob:
            x1 = largestblob[0].start
            x2 = largestblob[0].stop
            y1 = largestblob[1].start
            y2 = largestblob[1].stop

    boundingBox = [x1,y1,x2,y2]

    # draw bounding box
    if config.debugImageTitle:
        imbox = drawBoundingBox(im, boundingBox)
        cv2.imwrite(config.debugImageTitle + '_blobboundingbox.jpg', imbox)

    return boundingBox


def findBoundingBox(im, radius):
    "Find bounding box with expected target radius. Returns [x1,y1,x2,y2]"
    if radius < config.blobRadiusMax: # eg 10 pixels
        # use blob detector if radius<threshold
        boundingBox = findBoundingBoxByBlob(im)
    else:
        # use hough to find circle
        boundingBox = findBoundingBoxByCircle(im, radius)
    return boundingBox


#. do i need this anymore? was this before upgrading to v3?
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


if __name__ == "__main__":
    import lib
    orange = '../'+lib.getAdjustedFilepath('7206','C2684338','Clear')
    green = '../'+lib.getAdjustedFilepath('7206','C2684342','Green')
    blue = '../'+lib.getAdjustedFilepath('7206','C2684340','Violet')
    print orange
    channels = [
        ['Orange',orange,0.7,120,-65],
        ['Green',green,1,150,20],
        ['Blue',blue,1,0,0],
        ]
    im = combineChannels(channels)
    show(im)
    cv2.imwrite('foo.jpg',im)


