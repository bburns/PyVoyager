
"""
Image processing routines

Most of these are specific to PyVoyager
"""

import os
import os.path
import scipy.ndimage as ndimage # n-dimensional images - for blob detection
import numpy as np
import cv2
import math
import random

import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


import config
import lib
import log
import ransac




def cropImageFile(infile, outfile, tx=0, ty=0, scale=1.0):
    "crop/zoom in on image file - tx,ty are location of top-left corner in existing image"
    im = cv2.imread(infile, cv2.IMREAD_GRAYSCALE)
    im = cropImage(im, tx, ty, scale)
    cv2.imwrite(outfile, im)


def cropImage(im, tx=0, ty=0, scale=1.0):
    "crop/zoom in on image - tx,ty are location of top-left corner in existing image"
    im = shiftImage(im, tx,ty)
    M = np.float32([[scale,0,0],[0,scale,0]])
    # note: INTER_LINEAR (default) or INTER_CUBIC (slow) is preferred for zooming
    # see http://docs.opencv.org/trunk/da/d6e/tutorial_py_geometric_transformations.html
    # note: don't need to specify size/shape if not changing it - just pass None
    im = cv2.warpAffine(im, M, None, flags=cv2.INTER_CUBIC)
    return im


class Page:
    """
    wrapper around PIL text writing routines
    eg
        page = Page()
        page.vtab(5)
        page.println(title, color=200, center=True)
        page.save(filepath)
    """
    def __init__(self, size=800):
        "create a page to write on"
        self.size = size
        self.imgsize = [size,size] #.param - will be 1000x1000
        self.bgcolor = (0,0,0)
        self.img = Image.new("RGBA", self.imgsize, self.bgcolor)
        self.draw = ImageDraw.Draw(self.img)
        self.pos = [0,0]
        self.fontpath = config.titleFont
        self.fontsize = config.titleFontsize
        self.setfont(self.fontpath, self.fontsize)

    def htab(self, col):
        "horizontal tab"
        self.pos[0] = col * self.charWidth

    def vtab(self, row):
        "vertical tab"
        self.pos[1] = row * self.charHeight

    def setfont(self, fontpath=None, fontsize=None):
        "change font/size"
        fontpath = fontpath or self.fontpath
        fontsize = fontsize or self.fontsize
        self.font = ImageFont.truetype(fontpath, fontsize)
        self.charWidth, self.charHeight = self.font.getsize("M")
        self.charHeight *= 1.3 # fudge factor

    def println(self, s, color=160, center=False):
        "print a line or sequence of lines"
        lines = s.split('\n')
        fg = (color,color,color)
        for line in lines:
            w,h = self.font.getsize(line)
            if center:
                self.pos[0] = (self.size - w) / 2
            self.draw.text(self.pos, line, fg, font=self.font)
            # self.pos[1] = self.pos[1] + h*1.25
            self.pos[1] = self.pos[1] + self.charHeight

    def save(self, filepath):
        "save page to a file"
        self.img.save(filepath)


def thresholdImage(im):
    "get adaptive threshold of image"
    im = cv2.adaptiveThreshold(im, maxValue=255,
                               adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               thresholdType=cv2.THRESH_BINARY_INV,
                               blockSize=3,
                               C=10)
    return im


def getImageAlignment(im0, im1, dx=0, dy=0):
    """
    Get alignment between images using different methods available.
    Returns dx,dy,ok
    Returns 0,0,False if no alignment found
    """
    dx,dy,ok = getImageAlignmentORB(im0, im1)
    if not ok:
        dx,dy,ok = getImageAlignmentECC(im0, im1, dx=dx, dy=dy) # initialize with dx,dy
        # dx,dy,ok = getImageAlignmentDiff(im0, im1)
    return dx,dy,ok


def getImageAlignmentDiff(im0, im1):
    """
    get image alignment by minimizing the sum of differences between images
    #. this doesn't work very well yet
    """

    # lores image size
    # sz = 100
    sz = 200
    # sz = 40

    # tilesize = 40
    tilesize = 25
    # tilesize = 20
    # tilesize = 10

    # get lores versions
    im0sm = resizeImage(im0,sz,sz)
    im1sm = resizeImage(im1,sz,sz)
    show(im0sm)
    show(im1sm)

    dx=dy=0
    imax=jmax=sz-tilesize
    istep=1

    # get tile from im1
    nsteps = sz/tilesize
    dxsum=dysum=0
    for tilex in range(0,sz-tilesize,tilesize):
        for tiley in range(0,sz-tilesize,tilesize):
            tile = im1sm[tiley:tiley+tilesize, tilex:tilex+tilesize]
            # libimg.show(tile)

            # use opencv template matching routine
            # for examples of methods see
            # http://docs.opencv.org/3.1.0/d4/dc6/tutorial_py_template_matching.html
            # method = cv2.TM_SQDIFF
            # method = cv2.TM_SQDIFF_NORMED
            # method = cv2.TM_CCOEFF
            # method = cv2.TM_CCOEFF_NORMED
            # method = cv2.TM_CCORR
            method = cv2.TM_CCORR_NORMED
            res = cv2.matchTemplate(im0sm,tile,method)
            # res = cv2.matchTemplate(im1sm,tile,method) # sanity check
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            # top_left = min_loc
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            # w=h=tilesize
            # bottom_right = (top_left[0] + w, top_left[1] + h)
            # cv2.rectangle(res,top_left, bottom_right, 255, 1)
            # show(res)

            dx = top_left[0]-tilex
            dy = top_left[1]-tiley
            dxsum+=dx
            dysum+=dy

    dx = dxsum/nsteps/nsteps; dy = dysum/nsteps/nsteps
    dx *= 800/sz; dy *= 800/sz
    # dx,dy=dy,dx
    dx=-dx;dy=-dy
    # print dx,dy
    im1shifted = shiftImage(im1, dx,dy)
    show(im1shifted)
    return dx,dy,True


def getImageAlignmentORB(im0, im1):
    """
    Get alignment between images using ORB feature alignment.
    Returns dx,dy,alignmentOk
    If unable to align images returns 0,0,False
    """

    npoints = 500 # default
    # npoints = 100
    sz = 800
    # sz = 400
    # sz = 200
    # sz = 100
    # magnitude = True
    magnitude = False # best
    sharpen = False # best
    # sharpen = True
    contrast = True # best (using equalize hist)
    # contrast = False
    # neighborhood = 121
    # neighborhood = 51
    neighborhood = 31 # default and best
    # neighborhood = 21
    # neighborhood = 15
    # neighborhood = 13
    # neighborhood = 11
    # neighborhood = 9
    # neighborhood = 7
    # fastThreshold = 20 # default
    fastThreshold = 10 # best
    # fastThreshold = 5
    # fastThreshold = 1
    # fastThreshold = 0
    # knnMatching = True
    knnMatching = False # best
    crossCheck = True # best
    # crossCheck = False # need False so knnMatch works - why?
    # keepMatches = 50
    # keepMatches = 40
    # keepMatches = 30
    # keepMatches = 20
    keepMatches = 10 # best
    # keepMatches = 5
    transform = 'translate' # best
    # transform = 'affine'
    # transform = 'homography'

    # shrink image
    if sz!=800:
        im0 = resizeImage(im0,sz,sz)
        im1 = resizeImage(im1,sz,sz)

    if magnitude:
        im0 = getGradientMagnitude(im0)
        im1 = getGradientMagnitude(im1)

    if sharpen:
        im0 = sharpenImage(im0)
        im1 = sharpenImage(im1)

    if contrast:
        # three types of contrast enhancement - equalizeHist works best
        im0 = cv2.equalizeHist(im0)
        im1 = cv2.equalizeHist(im1)
        # ---
        # clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        # im0 = clahe.apply(im0)
        # im1 = clahe.apply(im1)
        # ---
        # maxIntensity = 255.0
        # phi = 1
        # theta = 1
        # expt = 2
        # x = np.arange(maxIntensity)
        # im0 = (maxIntensity/phi)*(im0/(maxIntensity/theta))**expt
        # im1 = (maxIntensity/phi)*(im1/(maxIntensity/theta))**expt
        # im0 = np.array(im0,dtype=np.uint8)
        # im1 = np.array(im1,dtype=np.uint8)

    # bug patch - see https://github.com/opencv/opencv/issues/6081
    cv2.ocl.setUseOpenCL(False)

    # Initiate ORB detector

    # ORB is basically a fusion of FAST keypoint detector and BRIEF descriptor
    # with many modifications to enhance the performance. First it use FAST to
    # find keypoints, then apply Harris corner measure to find top N points
    # among them. It also use pyramid to produce multiscale-features.

    # ORB (oriented BRIEF) keypoint detector and descriptor extractor.
    # described in [125] . The algorithm uses FAST in pyramids to detect stable
    # keypoints, selects the strongest features using FAST or Harris response,
    # finds their orientation using first-order moments and computes the
    # descriptors using BRIEF (where the coordinates of random point pairs (or
    # k-tuples) are rotated according to the measured orientation).
    # defaults:
    # create (int nfeatures=500, float scaleFactor=1.2f, int nlevels=8,
    #   int edgeThreshold=31, int firstLevel=0, int WTA_K=2,
    #   int scoreType=ORB::HARRIS_SCORE, int patchSize=31, int fastThreshold=20)
    # scaleFactor is for scaling the images down (or the detector patch
    # up) between octaves (or levels). for less calculations, use a
    # scaling of 1.5f and 4 levels.
    # orb = cv2.ORB_create()
    orb = cv2.ORB_create(npoints, edgeThreshold=neighborhood,
                         patchSize=neighborhood, fastThreshold=fastThreshold)

    # find the keypoints and their descriptors
    # kp0, des0 = orb.detectAndCompute(im0,None)
    # kp1, des1 = orb.detectAndCompute(im1,None)

    # detect keypoints
    kp0 = orb.detect(im0,None) # None is a mask you can pass
    kp1 = orb.detect(im1,None)

    # compute descriptors for keypoints
    kp0, des0 = orb.compute(im0,kp0)
    kp1, des1 = orb.compute(im1,kp1)

    # exit if no keypoints or descriptors found
    if des0 is None or des1 is None:
        print 'des0 or des1 is none - ie no keypoints found'
        return 0,0,False

    # out = cv2.drawKeypoints(im0,kp0,None)
    # show(out)

    # create brute force matcher
    # see http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_matcher/py_matcher.html
    # need to use NORM_HAMMING since ORB is a binary feature
    #. what exactly does crossCheck do?
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=crossCheck)

    if not knnMatching:
        # match descriptors and sort them in order of distance
        matches = matcher.match(des0,des1)
        matches = sorted(matches, key = lambda x:x.distance)
        good = matches[:keepMatches]
    else:
        # use K nearest neighbor matching
        matches = matcher.knnMatch(des0,des1,k=2)
        # get all the good matches as per Lowe's ratio test
        good = [m[0] for m in matches if len(m) == 2 and m[0].distance < m[1].distance * 0.75]
    # print 'good matches',len(good)

    # draw good matches
    # shows images side by side with colored lines between matched points
    #........... make debug flag to save this image to a debug folder? useful to look through them
    # out = cv2.drawMatches(im0,kp0,im1,kp1,good,None,
                          # flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # show(out)

    # find transformation matrix
    if transform=='translate':

        # simple translation (x,y shift)

        # get simple translation model - includes ransac outlier elimination
        pts0 = [kp0[m.queryIdx].pt for m in good]
        pts1 = [kp1[m.trainIdx].pt for m in good]
        data = zip(pts0,pts1)
        dx, dy, modelOk = ransac.getRansacModel(data)
        if not modelOk:
            print 'no ransac model found'
            return 0,0,False
        # imx = cv2.warpAffine(im1, M, (cols,rows),
        #                      flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        imx = shiftImage(im1, dx, dy)
        # show(imx)
        blank = np.zeros((sz,sz),np.uint8)
        # imy = cv2.merge((blank, im0, imx))
        imy = cv2.merge((im0, blank, imx)) # base image is blue, moved is red
        # show(imy)

    elif transform=='affine':

        # Affine transformation (shift, rotation, scaling, shear)

        # note: M might include a bit of rotation, but we'll just ignore that
        # this includes RANSAC to eliminate outliers - see
        # https://github.com/opencv/opencv/blob/master/modules/video/src/lkpyramid.cpp
        pts0 = np.float32([ kp0[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        pts1 = np.float32([ kp1[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        M = cv2.estimateRigidTransform(pts0, pts1, False)
        if M is None:
            print 'M is none - no good solution found'
            return 0,0,False
        # print M
        # eg
        # [[  1.00273314e+00   2.62991563e-03  -1.53541381e+02]
        # [ -2.62991563e-03   1.00273314e+00  -1.77198771e+01]]
        # show images
        # # just want pure translation
        # M[0][0]=1
        # M[0][1]=0
        # M[1][0]=0
        # M[1][1]=1
        # # note order of cols, rows -
        # rows, cols = im1.shape[:2]
        # imx = cv2.warpAffine(im1, M, (cols,rows),
        #                      flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        # show(imx)
        # blank = np.zeros((sz,sz),np.uint8)
        # imy = cv2.merge((blank, im0, imx))
        # show(imy)
        dx = M[0][2]
        dy = M[1][2]

    elif transform=='homography':

        # Homography transform (shift, rotate, scale, skew, tilt)

        # initialize arrays of keypoint coordinates
        pts0list = []
        pts1list = []
        for m in good:
            # get the matching keypoints for each of the images
            im0idx = m.queryIdx
            im1idx = m.trainIdx
            # get the coordinates
            (x0,y0) = kp0[im0idx].pt
            (x1,y1) = kp1[im1idx].pt
            # append to each list
            pts0list.append((x0, y0))
            pts1list.append((x1, y1))
        pts0 = np.array(pts0list)
        pts1 = np.array(pts1list)

        # see http://docs.opencv.org/2.4/modules/calib3d/doc/
        #   camera_calibration_and_3d_reconstruction.html#findhomography
        H, status = cv2.findHomography(pts0, pts1, cv2.RANSAC, 5.0) #. 5.0=?
        if H is None:
            print 'H is none - no good solution found - %d good matches' % len(good)
            return 0,0,False
        print H
        # imx = shiftImage(im1, dx, dy)
        # # show(imx)
        # blank = np.zeros((sz,sz),np.uint8)
        # imy = cv2.merge((blank, im0, imx))
        # # show(imy)
        dx = H[0][2]
        dy = H[1][2]

    # return results
    if sz!=800: dx*=800/sz;dy*=800/sz #.params
    alignmentOk = True
    return dx,dy,alignmentOk


def sharpenImage(im):
    "sharpen image with a simple 2d kernel"
    kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
    # kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) # a bit too sharp, even for clouds
    # kernel = np.array([[-1,-1,-1,-1,-1],
                       # [-1,2,2,2,-1],
                       # [-1,2,8,2,-1],
                       # [-1,2,2,2,-1],
                       # [-1,-1,-1,-1,-1]]) / 8.0
    # kernel = np.array([[1,1,1], [1,-7,1], [1,1,1]]) # blur
    im = cv2.filter2D(im, -1, kernel)
    return im


def imwrite(outfile, im):
    """
    like cv2.imwrite but on error will try to create the outfile's folder also.
    useful in some cases where not known if folder exists or not.
    """
    ok = cv2.imwrite(outfile, im)
    if not ok:
        folder = os.path.dirname(outfile)
        lib.mkdir(folder)
        ok = cv2.imwrite(outfile, im)
    return ok


def inpaintImage(infile, priorfile, outfile, targetRadius):
    """
    fill in regions of black or white inside targetRadius in infile using pixels from priorfile.
    assumes both files are centered on the target.
    targetRadius is the expected size of the target.
    """
    debug = False

    # read image and prior image
    im = cv2.imread(infile, 0) #.param
    imPrior = cv2.imread(priorfile, 0) #.param
    if debug: show(im)
    if debug: show(imPrior)

    # get mask for target radius
    maskTarget = np.zeros(im.shape[:2], np.uint8)
    maskTarget = cv2.circle(maskTarget, (399,399), targetRadius, 255, -1) # -1=filled #.params
    if debug: show(maskTarget)

    # get mask where image is black
    maskBlack = np.array(255 * (im<=4), np.uint8) #.param
    if debug: show(maskBlack)

    # get mask where image is white
    maskWhite = np.array(255 * (im>=255), np.uint8) #.param
    if debug: show(maskWhite)

    # combine the masks
    maskEmpty = maskBlack | maskWhite
    if debug: show(maskEmpty)

    # merge with target mask
    maskPaint = maskTarget & maskEmpty
    if debug: show(maskPaint)

    # pull pixels from imPrior where mask is
    imOut = (im & (255-maskPaint)) + (imPrior & maskPaint)
    if debug: show(imOut)

    # cv2.imwrite(outfile, imOut)
    imwrite(outfile, imOut)


def getGradientMagnitude(im):
    "Get magnitude of gradient for given image using simple kernel"

    ddepth = cv2.CV_32F

    kernel = np.zeros((1,3))
    kernel[0][0]=-1
    kernel[0][1]=0
    kernel[0][2]=1
    dx = cv2.filter2D(im, ddepth, kernel)
    dxabs = cv2.convertScaleAbs(dx)

    kernel = np.zeros((3,1))
    kernel[0][0]=-1
    kernel[1][0]=0
    kernel[2][0]=1
    dy = cv2.filter2D(im, ddepth, kernel)
    dyabs = cv2.convertScaleAbs(dy)

    mag = cv2.addWeighted(dxabs, 0.5, dyabs, 0.5, 0)
    return mag


def getGradientMagnitudeSobel(im):
    """
    Calculate the x and y gradients using Sobel operator.
    Sobel includes Gaussian filtering, so may not be ideal for detecting noise.
    """
    # ddepth = cv2.CV_32F
    # dx = cv2.Sobel(im, ddepth, 1, 0)
    # dy = cv2.Sobel(im, ddepth, 0, 1)
    #. wouldn't ksize=3 just make it same as previous fn (with [-1 0 1] kernels)?
    dx = cv2.Sobel(im, ddepth, 1, 0, ksize=3)
    dy = cv2.Sobel(im, ddepth, 0, 1, ksize=3)
    # Combine the two gradients
    mag = cv2.addWeighted(np.absolute(dx), 0.5, np.absolute(dy), 0.5, 0)
    return mag


def annotateImageFile(infile, outfile, imageId, time, distance, note):

    """
    Overlay some information on given input file and write to outfile
    """

    font = ImageFont.truetype(config.annotationsFont, config.annotationsFontsize)
    fgcolor = (200,200,200)
    w,h = font.getsize('M')

    img = Image.open(infile)
    if img!='RGB': img = img.convert('RGB') # else some images cause TypeError on draw text

    draw = ImageDraw.Draw(img)

    pos = (50,625)

    s = imageId
    draw.text(pos, s, fgcolor, font=font)
    pos = (pos[0],pos[1]+int(h*1.5))

    s = time
    draw.text(pos, s, fgcolor, font=font)
    pos = (pos[0],pos[1]+int(h*1.5))

    s = distance
    draw.text(pos, s, fgcolor, font=font)
    pos = (pos[0],pos[1]+int(h*1.5))

    s = note
    draw.text(pos, s, fgcolor, font=font)
    pos = (pos[0],pos[1]+int(h*1.5))

    img.save(outfile)


def denoiseImageFile(infile, outfile):

    """
    attempt to remove noise from the given image file and save to outfile
    """

    im = cv2.imread(infile, 0) #.param

    # blank out bottom 3 pixels
    im[-3:,:] = 0

    # blank out right 3 pixels
    im[:,-3:] = 0

    # nowork - blurs some nice images - jupiter, triton ice
    # remove salt and pepper noise, and thin lines
    # im = cv2.medianBlur(im, 5)

    # nowork - inpainting doesn't look very good
    # remove larger blocks of noise by inpainting
    # first detect regions with lots of variation
    # mag = getGradientMagnitude(im)
    # mask = cv2.adaptiveThreshold(im, maxValue=255,
    #                              adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                              thresholdType=cv2.THRESH_BINARY_INV,
    #                              blockSize=3,
    #                              C=8)
    # # ret, mask = cv2.threshold(im, 200, 255, cv2.THRESH_BINARY) # nope
    # # kernel = np.ones((5,1),np.uint8)
    # kernel = np.ones((10,1),np.uint8)
    # mask = cv2.dilate(mask, kernel, iterations = 1)
    # # im = cv2.inpaint(im, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    # im = cv2.inpaint(im, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)


    # black out large blocks of noise

    # # detect contours of noisy areas
    # mask = cv2.adaptiveThreshold(im, maxValue=255,
    #                              adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                              thresholdType=cv2.THRESH_BINARY_INV,
    #                              blockSize=3,
    #                              C=11)
    # kernel = np.ones((2,21), np.uint8)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # dilate then erode
    # # find contours and bounding boxes, pick out rectangular ones and black whole rectangle out
    # im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # for contour in contours:
    #     x,y,w,h = cv2.boundingRect(contour)
    #     if w>100 and w>h*3:
    #         cv2.rectangle(im, (x,y), (x+w,y+h), 0, -1) # filled black rectangle

    #
    mask = getGradientMagnitude(im)
    mask = cv2.adaptiveThreshold(mask, maxValue=255,
                               adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               thresholdType=cv2.THRESH_BINARY_INV,
                               blockSize=3,
                               # C=25)
                               C=30)
    # this extracts any long horizontal segments
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (120,1));
    mask = cv2.dilate(mask, kernel)
    # this __
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,5));
    mask = cv2.dilate(mask, kernel)
    mask = cv2.erode(mask, kernel)
    im = im & (255-mask)


    # try removing noise near sharp edges (median blur)
    # the larger C is, the less noise will be removed
    mask = cv2.adaptiveThreshold(im, maxValue=255,
                                 adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 thresholdType=cv2.THRESH_BINARY_INV,
                                 blockSize=3,
                                 # C=2) # ends up blurring triton
                                 # C=5) # leaves too much noise
                                 C=4) # good compromise
    kernel = np.ones((5,5), np.uint8) # expand edges horizontally
    mask = cv2.dilate(mask, kernel, iterations = 1) # expand edge mask
    mask = cv2.medianBlur(mask, 5) # remove dots from mask
    imblurred = cv2.medianBlur(im, 5) # remove noise from image
    im = im + ((imblurred - im) & mask) # combine image with blurred version


    # nowork
    # # fill in single pixel horizontal lines
    # # first identify horizontal segments - then get avg of above and below pixels
    # linesToFill = []
    # im2 = im
    # for j in xrange(0,800):
    #     rowMiddle = im[j,:]
    #     # rowAbove = im[j-1,:] if j>0 else np.zeros(800,np.uint8)
    #     # rowBelow = im[j+1,:] if j<799 else np.zeros(800,np.uint8)
    #     rowAbove = im2[j-1,:] if j>0 else np.zeros(800,np.uint8)
    #     rowBelow = im2[j+1,:] if j<799 else np.zeros(800,np.uint8)
    #     maxlen = 0
    #     seglen = 0
    #     for i in xrange(0,800):
    #         above = rowAbove[i]
    #         middle = rowMiddle[i]
    #         below = rowBelow[i]
    #         # d1 = middle-above
    #         # d2 = middle-below
    #         # if (middle>above and middle>below) or (middle<above and middle<below):
    #         # eps=30
    #         # above = above + eps
    #         # below = below + eps
    #         if (middle>above and middle>below):
    #             seglen += 1
    #             if seglen>maxlen:
    #                 maxlen = seglen
    #         else:
    #             seglen = 0
    #     # if maxlen > 20: #.param
    #     if maxlen > 30: #.param
    #         linesToFill.append(j)
    # for line in linesToFill:
    #     rowAbove = im[line-1,:] if line>0 else np.zeros(800,np.uint8)
    #     rowBelow = im[line+1,:] if line<799 else np.zeros(800,np.uint8)
    #     # im[line,:] = 0
    #     im[line,:] = (rowAbove+rowBelow)/2

    # cv2.imwrite(outfile, im)
    imwrite(outfile, im)


def resizeImage(im, w, h):
    "Resize image, keeping aspect ratio, filling in gaps with black, return new image."

    oldH, oldW = im.shape[:2]
    aspectRatio = float(oldW) / float(oldH)
    if aspectRatio > 1: # width>height
        newW = w
        newH = int(newW / aspectRatio)
    else:
        newH = h
        newW = int(newH * aspectRatio)
    # scale the image
    # http://docs.opencv.org/trunk/da/d6e/tutorial_py_geometric_transformations.html
    zooming = (newW<w) or (newH<h)
    if zooming:
        # INTER_LINEAR and INTER_CUBIC (slow) is preferred for zooming
        # note: this takes w,h not h,w!
        # im = cv2.resize(im, (newW,newH), interpolation=cv2.INTER_AREA)
        im = cv2.resize(im, (newW,newH), interpolation=cv2.INTER_CUBIC)
    else:
        # INTER_AREA is preferred for shrinking
        im = cv2.resize(im, (newW,newH), interpolation=cv2.INTER_AREA)

    # add the new image to a blank canvas
    canvas = np.zeros(im.shape, np.uint8)
    x = int((w-newW)/2)
    y = int((h-newH)/2)
    canvas[y:y+newH, x:x+newW] = im
    return canvas


def getImageAlignmentECC(imFixed, im, dx=0, dy=0):
    """
    Get alignment between images using ECC maximization algorithm.
    Returns dx,dy,alignmentOk
    If unable to align images returns 0,0,False
    """

    mode = cv2.MOTION_TRANSLATION
    M = np.eye(2, 3, dtype=np.float32) #. add paramnames
    # can pass in initial guess
    M[0][2] = dx
    M[1][2] = dy
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                config.stabilizeECCIterations, config.stabilizeECCTerminationEpsilon)

    # run the ECC algorithm
    # throws an error if doesn't converge, so catch it
    try:
        cc, M = cv2.findTransformECC(imFixed, im, M, mode, criteria)
    except Exception, e:
        print 'exception', e
        # if can't find solution, images aren't close enough in similarity
        dx = 0
        dy = 0
        alignmentOk = False
    else:
        # eg
        # print M
        # [[ 1.          0.          1.37005 ]
        #  [ 0.          1.          0.485788]]
        dx = M[0][2]
        dy = M[1][2]
        dx = int(round(dx))
        dy = int(round(dy))
        alignmentOk = True
    return dx,dy,alignmentOk


def stabilizeImageFile(infile, outfile, targetRadius):
    """
    Stabilize infile against disc of radius targetRadius and write to outfile.
    Returns dx,dy,stabilizationOk
    targetRadius is the expected radius, in pixels
    """

    # get fixed image of filled target disc
    imFixed = np.zeros((800,800), np.uint8) #.params
    cv2.circle(imFixed, (399,399), targetRadius, 255, -1) # -1=filled #.params

    # get input file
    im = cv2.imread(infile, cv2.IMREAD_GRAYSCALE)

    # align the image to the target disc
    # dx, dy, alignmentOk = getImageAlignment(imFixed, im)
    dx, dy, alignmentOk = getImageAlignmentECC(imFixed, im)
    if alignmentOk:
        im = shiftImage(im, dx, dy)
        # this doesn't work as precisely (why?), and it's about same speed, so just use warp
        # im = translateImage(im, dx, dy)
    #. bug - these flags kept getting set to True, but where?
    # print config.drawCrosshairs, config.drawTarget
    # if config.drawCrosshairs:
    #     drawCrosshairs(im)
    # if config.drawTarget:
    #     im = gray2rgb(im)
    #     circle = (399,399,targetRadius) #.params
    #     drawCircle(im, circle, color = (0,255,255)) # yellow circle
    imwrite(outfile, im)
    return dx,dy,alignmentOk


def translateImage(im, dx, dy):
    "translate an image by the given delta x,y, keeping same image size"
    #. eliminate this
    # see also shiftImage, which works better
    cx = int(im.shape[1]/2)
    cy = int(im.shape[0]/2)
    x = int(cx - dx)
    y = int(cy - dy)
    boundingBox = [x,y,x,y]
    im = centerImage(im, boundingBox)
    return im


def centerImageFileAt(infile, outfile, x, y):
    """
    Center the given image file at the given x,y and save it to outfile.
    """
    im = cv2.imread(infile, cv2.IMREAD_GRAYSCALE)
    # center the image on the target
    boundingBox = [x,y,x,y]
    im = centerImage(im, boundingBox)
    if config.drawCrosshairs:
        drawCrosshairs(im)
    imwrite(outfile, im)


def centerImageFile(infile, outfile, targetRadius=None):
    """
    Center the given image file on a target and save it to outfile.
    Returns x,y,foundRadius
    """

    im = cv2.imread(infile, cv2.IMREAD_GRAYSCALE)

    # find the bounding box of biggest object
    # either a blob or a circle
    boundingBox = findBoundingBox(im, targetRadius)

    # center the image on the target
    im = centerImage(im, boundingBox)

    imwrite(outfile, im)

    x = int((boundingBox[0] + boundingBox[2])/2)
    y = int((boundingBox[1] + boundingBox[3])/2)
    # this is pretty approximate when it's just a blob
    foundRadius = int((boundingBox[2]-x + boundingBox[3]-y)/2)
    return x, y, foundRadius


def drawCrosshairs(im):
    "draw crosshairs on given image"
    color = 64
    xmax = im.shape[1]
    ymax = im.shape[0]
    cx = int(xmax/2)
    cy = int(ymax/2)
    im[cy, 0:xmax-1] = color
    im[0:ymax-1, cx] = color


def img2png(srcdir, filespec, destdir):
    "Convert all IMG files matching filespec in srcdir to PNG files in destdir"

    # first convert img's to png's, then move them to the dest dir
    savedir = os.getcwd()
    os.chdir(srcdir)
    # eg "img2png *CALIB.img -fnamefilter > nul"
    cmd = "img2png " + filespec + " " + config.img2pngOptions + " > nul"
    os.system(cmd)

    # now move the png files to destdir
    #. use os.rename - should be faster
    # (srcdir is relative to the python program so need to switch back to that dir)
    os.chdir(savedir)
    # cmd = "mv " + srcdir +"*.png " + destdir + " > nul" # nowork on windows due to backslashes
    cmd = "move " + srcdir +"\\*.png " + destdir + " > nul"
    os.system(cmd)


# def stretchHistogram(im, nHotPixels=100):
def stretchHistogram16to8bit(im, maxvalue=None):
    """
    stretch the histogram of the given 16bit image and return it as an 8bit image.
    hot pixels are set at 32767, but hot noise can exist in an image also.
    can pass maxvalue
    """

    # get histogram
    # see http://docs.opencv.org/3.1.0/d1/db7/tutorial_py_histogram_begins.html
    # eg hist = cv2.calcHist([im],[0],mask,[256],[0,256])
    images = [im]
    channels = [0]
    mask = None # lets you filter to part of an image
    histSize = [256] # number of bins
    # ranges = [0, 256] # range of intensity values
    ranges = [0, 32768] # range of intensity values
    hist = cv2.calcHist(images, channels, mask, histSize, ranges)
    # print [int(x) for x in hist]

    # # ignore top n pixels
    # # start at top, get cumulative sum downwards until reach certain amount of pixels
    # npixels = im.shape[0] * im.shape[1]
    # sum = 0
    # maxvalue = 255
    # for i in xrange(255,0,-1):
    #     sum += hist[i]
    #     if sum > nHotPixels:
    #         maxvalue = i
    #         break

    # if no override value given, scan down histogram from hot pixel value 255,
    # set max level to be next lowest value
    if maxvalue is None:
        maxvalue = 254
        for i in xrange(254,0,-1):
            # if hist[i]>0:
            # see config.py for more info
            if hist[i] > config.adjustHistogramHotPixelCountCutoff:
                maxvalue = i
                break

    # print maxvalue
    maxvalue = maxvalue * 128

    # set values > maxvalue to maxvalue
    # see http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html
    np.clip(im, 0, maxvalue, im)

    # convert 16-bit to 8-bit if needed (otherwise the histogram stretching gets posterized)
    if type(im[0][0])==np.uint16:
        # stretch image values to brightest amount
        im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
        # max level in the 16-bit image is 32767, and (/ 32767 128) = 255
        # im = im / 128 # this can be dividing it by too much - using normalize is safer
        im = np.array(im, np.uint8)

    return im


# def adjustImageFile(infile, outfile, doStretchHistogram=True):
def adjustImageFile(infile, outfile, maxvalue=None):
    """
    Adjust the given image file and save it to outfile - stretch histogram and rotate 180deg.
    """

    # need ANYDEPTH flag as the pngs are 16-bit
    im = cv2.imread(infile, cv2.IMREAD_GRAYSCALE | cv2.IMREAD_ANYDEPTH)

    # stretch the histogram to bring up the brightness levels (the CALIB images are dark)
    # if doStretchHistogram:
        # im = stretchHistogram(im)
    im = stretchHistogram16to8bit(im, maxvalue)

    # rotate image by 180
    im = np.rot90(im, 2)

    retval = imwrite(outfile, im)
    return retval


def show(im, title='cv2 image - press esc to continue'):
    "Show a cv2 image and wait for a keypress"
    if im.shape[1]>680:
        im = resizeImage(im,int(im.shape[1]*0.75),int(im.shape[0]*0.75)) # might be nonsquare
    cv2.imshow(title, im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def shiftImage(im, dx, dy):
    """
    Shift the image by dx, dy using an Affine matrix.
    Note: image dimensions are kept the same - the image is just shifted out of frame.
    """
    M = np.array([[1,0,dx],[0,1,dy]], np.float)
    rows, cols = im.shape[:2]
    # note order of cols, rows -
    im = cv2.warpAffine(im, M, (cols, rows), flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    return im


#. make this more generic - eg pass in set of images to align, return set of displacements
# could call it getChannelAlignments
def alignChannels(channels):
    "attempt to align the images in the given channel arrays"
    # print channels
    # print [ch[2:-1] for ch in channels if ch]
    im0 = channels[0][config.colChannelIm]
    im1 = channels[1][config.colChannelIm]
    assert not im0 is None
    assert not im1 is None
    dx,dy,alignmentOk = getImageAlignment(im0, im1)
    if alignmentOk:
        channels[1][config.colChannelX] = dx
        channels[1][config.colChannelY] = dy
    if channels[2]:
        im2 = channels[2][config.colChannelIm]
        assert not im2 is None
        dx,dy,alignmentOk = getImageAlignment(im0, im2)
        if alignmentOk:
            channels[2][config.colChannelX] = dx
            channels[2][config.colChannelY] = dy
    # for channel in channels:
    #     if channel: print channel[2:-1]
    return channels


#. refactor
def getCanvasSizeForChannels(channels):
    "given an array of channels, return size of canvas that would contain them all"
    xmin = 0; xmax = 799; ymin = 0; ymax = 799 #.params
    for row in channels:
        if row:
            x = row[config.colChannelX] if len(row)>config.colChannelX else 0
            y = row[config.colChannelY] if len(row)>config.colChannelY else 0
            if x < xmin: xmin = x
            if x+799 > xmax: xmax = x+799 #.param
            if y < ymin: ymin = y
            if y+799 > ymax: ymax = y+799 #.param
    w = xmax-xmin+1; h = ymax-ymin+1
    enlarged = (w!=800) or (h!=800) #.param
    return w,h,xmin,ymin,enlarged


#. refactor
def combineChannels(channels, optionAlign=False):
    """
    Combine the given channels and return a single cv2 image.
    channels is an array of [fileId, filter, filename, weight, x, y]
    eg channels = [
      ['c1234','Orange','composites/orange.png',1,0,0],
      ['c1235','Green','composites/green.png',0.8,30,40],
      ['c1236','Blue','composites/blue.png',0.9,50,66],
    ]
    If only one channel included will return a b/w image.
    If missing a channel will use a blank/black image for that channel.
    If optionAlign is True will attempt to align channels - x,y values
    are included in the return channels array.
    Returns im, channels.
    """
    # print channels

    # if just one channel then return a bw image
    if len(channels)==1:
        filename = channels[0][config.colChannelFilename]
        gray = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        if optionAlign:
            channels[0][config.colChannelX] = 0
            channels[0][config.colChannelY] = 0
        return gray, channels

    # # find size of canvas that will contain all images
    # w,h,enlarged = getCanvasSizeForChannels(channels)

    # # get images for each channel
    # rowRed = None
    # rowGreen = None
    # rowBlue = None
    # for row in channels:
    #     filename = row[colFilename]
    #     # note: this returns None if filename is invalid - doesn't throw an error
    #     #. this is wasteful - might not even use this file
    #     im = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    #     # apply weight if necessary
    #     weight = row[colWeight] if len(row)>colWeight else 1.0
    #     if weight!=1.0: im = cv2.multiply(im,weight)
    #     # if canvas needs to be enlarged, do so
    #     if enlarged:
    #         canvas = np.zeros((h,w), np.uint8) # 0-255
    #         x = row[config.colChannelX] if len(row)>config.colChannelX else 0
    #         y = row[config.colChannelY] if len(row)>config.colChannelY else 0
    #         # print xmin,x,ymin,y
    #         # copy image into canvas at right point
    #         canvas[y-ymin:y-ymin+800, x-xmin:x-xmin+800] = im
    #         im = canvas
    #         # show(im)
    #     row.append(im)
    #     # now assign the row to one of the available channels
    #     # eventually would like something more accurate than just rgb.
    #     # and note: the last one in the set of channels wins.
    #     filter = row[config.colChannelFilter]
    #     if filter in ['Orange']:
    #         rowRed = row
    #     if filter in ['Green']:
    #         rowGreen = row
    #     if filter in ['Blue','Violet','Uv','Ch4_Js','Ch4_U']:
    #         rowBlue = row

    # # assign a blank image if missing a channel
    # blank = np.zeros((h,w), np.uint8)
    # imRed = rowRed[colIm] if rowRed else blank
    # imGreen = rowGreen[colIm] if rowGreen else blank
    # imBlue = rowBlue[colIm] if rowBlue else blank

    # # merge channels - BGR for cv2
    # print imBlue.shape
    # print imGreen.shape
    # print imRed.shape
    # # if imBlue.shape[0]!=800: imBlue = resizeImage(imBlue,800,800)
    # # if imGreen.shape[0]!=800: imGreen = resizeImage(imGreen,800,800)
    # # if imRed.shape[0]!=800: imRed = resizeImage(imRed,800,800)
    # im = cv2.merge((imBlue, imGreen, imRed))
    # # show(im)

    # get dictionary of filters
    d = {}
    for row in channels:
        filter = row[config.colChannelFilter]
        d[filter] = row

    # a little dictionary fn
    def dget(d, skeys):
        "pop a value from dictionary d, trying all keys in skeys"
        if len(d)>0:
            keys = skeys.split(',')
            for key in keys:
                value = d.pop(key, None)
                if value:
                    return value
        return None

    # first pass - assign primary colors, if available
    channelBlue = dget(d,'Blue')
    channelRed = dget(d,'Orange')
    channelGreen = dget(d,'Green')

    # second pass - choose from some secondary options
    # Ch4 are in infrared
    if channelBlue is None: channelBlue = dget(d,'Violet,Uv,Ch4_Js,Ch4_U,Green,Orange')
    if channelRed is None: channelRed = dget(d,'Ch4_Js,Ch4_U,Blue,Violet,Uv,Green')
    if channelGreen is None: channelGreen = dget(d,'Ch4_Js,Ch4_U,Orange,Blue,Violet,Uv')

    # third pass - anything can use the clear channel
    blankrow = ['blank','Blank','blank.jpg',1,0,0]
    if channelBlue is None: channelBlue = d.get('Clear') or blankrow
    if channelRed is None: channelRed = d.get('Clear') or blankrow
    if channelGreen is None: channelGreen = d.get('Clear') or blankrow

    # get images
    blank = np.zeros((800,800), np.uint8) #.params
    for row in [channelBlue, channelRed, channelGreen]:
        if row:
            # print row
            filename = row[config.colChannelFilename]
            im = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            if im is None: im = blank
            # apply weight if necessary
            weight = row[config.colChannelWeight]
            if weight!=1.0: im = cv2.multiply(im,weight)
            #. handle this
            # # if canvas needs to be enlarged, do so
            # if enlarged:
            #     canvas = np.zeros((h,w), np.uint8) # 0-255
            #     x = row[config.colChannelX] if len(row)>config.colChannelX else 0
            #     y = row[config.colChannelY] if len(row)>config.colChannelY else 0
            #     # print xmin,x,ymin,y
            #     # copy image into canvas at right point
            #     canvas[y-ymin:y-ymin+800, x-xmin:x-xmin+800] = im
            #     im = canvas
            #     # show(im)
            # stick the image on the end of the row (colIm)
            row.append(im)

    # # fourth pass - assume we have at least 2 channels at this point,
    # # so try synthesizing a third.
    # # . this doesn't work very well - better to have a dedicated colorize step
    # imRed = channelRed[config.colChannelIm] if channelRed else None
    # imGreen = channelGreen[config.colChannelIm] if channelGreen else None
    # imBlue = channelBlue[config.colChannelIm] if channelBlue else None
    # if imBlue is None: imBlue = (imRed + imGreen) / 2
    # if imRed is None: imRed = (imBlue + imGreen) / 2
    # if imGreen is None: imGreen = (imRed + imBlue) / 2

    # attempt to align channels
    if optionAlign:
        channels = alignChannels([channelBlue, channelRed, channelGreen])

    # find size of canvas that will contain all images
    w,h,xmin,ymin,enlarged = getCanvasSizeForChannels(channels)
    # print w,h,xmin,ymin,enlarged

    # if canvas needs to be enlarged, do so, and position each channel correctly
    if enlarged:
        for row in channels:
            if row: #.remove
                im = row[config.colChannelIm]
                x = row[config.colChannelX]
                y = row[config.colChannelY]
                im = shiftImage(im, x, y)
                row[config.colChannelIm] = im

    # assign a blank image if missing a channel
    blank = np.zeros((h,w), np.uint8)
    imRed = channelRed[config.colChannelIm] if channelRed else blank
    imGreen = channelGreen[config.colChannelIm] if channelGreen else blank
    imBlue = channelBlue[config.colChannelIm] if channelBlue else blank

    # merge channels
    # print imBlue.shape
    # print imGreen.shape
    # print imRed.shape
    im = cv2.merge((imBlue, imGreen, imRed)) # BGR for cv2
    # show(im)

    # scale image to 800x800
    if enlarged:
        im = resizeImage(im, 800, 800) #.params
        # show(im)

    return im, channels


def drawCircle(im, circle, color = (0,255,0)):
    """
    Draw a circle on the given cv2 image.
    Note: circle is (x,y,radius), color is (b,g,r).
    """
    (x,y,r) = circle
    lineWidth = 1
    cv2.circle(im, (x,y), r, color, lineWidth)


def gray2rgb(im):
    "convert a gray cv2 image to rgb, return new image"
    im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
    return im


def rgb2gray(im):
    "convert an rgb image to gray, return new image"
    im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    return im


def drawBoundingBox(im, boundingBox):
    "draw a box on image, return new image"
    [x1,y1,x2,y2] = boundingBox
    imbox = np.copy(im)
    imbox = cv2.cvtColor(imbox, cv2.COLOR_GRAY2RGB)
    cv2.rectangle(imbox, (x1,y1),(x2,y2), (255,0,0), 2)
    return imbox


def findCircle(im, expectedRadius=None):
    """
    Find best circle in given image, with optional expectedRadius of target.
    Returns circle as (x,y,r)
    """

    # set Hough circle detection parameters

    # Note: internally the HoughCircles function calls the Canny edge detector

    # only available method now
    method = cv2.HOUGH_GRADIENT # if get error here, upgrade to OpenCV v3

    # size of accumulator space relative to input image
    dp = config.houghAccumulatorSize # eg 1.0

    # distance between circles
    minDist = config.houghMinDistanceBetweenCircles # eg 200px

    # First method-specific parameter. In case of CV_HOUGH_GRADIENT,
    # it is the higher threshold of the two passed to the Canny() edge
    # detector (the lower one is twice smaller).
    # higher value means edges need to be sharper
    # this value will be lowered if no circles found
    canny_threshold = config.houghCannyUpperThreshold # eg 200

    # the accumulator threshold for the circle centers at the detection
    # stage. The smaller it is, the more false circles may be detected. Circles
    # corresponding to the larger accumulator values, will be returned first.
    # This will set how many edge points it needs to find to
    # declare that it's found a circle. Again, too high will detect nothing, too
    # low will declare anything to be a circle. The ideal value of param 2 will
    # be related to the circumference of the circles.
    #. so should be proportional to the expectedRadius?
    acc_threshold = config.houghAccumulatorThreshold # eg 10

    # get search radii
    if expectedRadius:
        pct = config.houghRadiusSearchPercent # eg 10
        minRadius = int((1-float(pct)/100) * expectedRadius)
        maxRadius = int((1+float(pct)/100) * expectedRadius)
    else:
        minRadius = 0
        maxRadius = 0

    # look for circles, lowering canny threshold if can't find any (ie assume target is dim)
    circles = None
    while circles is None:
        circles = cv2.HoughCircles(im, method, dp, minDist,
                                   param1 = canny_threshold,
                                   param2 = acc_threshold,
                                   minRadius = minRadius,
                                   maxRadius = maxRadius)
        if circles is None:
            canny_threshold = int(canny_threshold / 2)
            # log.log('reducing canny threshold to',canny_threshold)
            if canny_threshold < 20: #. param
                break

    # draw canny edges
    if config.debugImageTitle:
        upper = canny_threshold
        lower = upper / 2 # this is what HoughCircles uses
        imedges = cv2.Canny(im, lower, upper)
        cv2.imwrite(config.debugImageTitle + '_cannyedges.jpg', imedges)

    if circles is None:
        # log.log('no circles found')
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
    return circle # (x,y,r)


def centerImage(im, boundingBox):
    "center image on bounding box, crop to it, return new image"

    [x1,y1,x2,y2] = boundingBox
    cx = int((x1+x2)/2.0)
    cy = int((y1+y2)/2.0)

    # reverse these
    imwidth = im.shape[1]
    imheight = im.shape[0]

    # make a bigger canvas to place image im on
    newsize = (imheight * 2, imwidth * 2)
    canvas = np.zeros(newsize, np.uint8) # defaults to float

    # put image on canvas centered on bounding box
    # eg canvas[800-cx:1600-cx, 800-cy:1600-cy] = np.array(im)
    canvas[imheight-cy : imheight-cy+imheight, imwidth-cx : imwidth-cx+imwidth] = im

    # crop canvas to original image size
    # eg imcrop = canvas[400:1200, 400:1200]
    x1 = int(imwidth/2)
    y1 = int(imheight/2)
    # imcrop = canvas[x1:x1+imwidth, y1:y1+imheight]
    imcrop = canvas[y1:y1+imheight, x1:x1+imwidth]

    return imcrop


def findBoundingBoxByCircle(im, radius):
    "Find the bounding box enclosing the best circle in image and return it, or None."
    circle = findCircle(im, radius)
    if not circle is None:
        (x,y,r) = circle
        x1 = x-r
        x2 = x+r
        y1 = y-r
        y2 = y+r
        boundingBox = [x1,y1,x2,y2]
    else:
        # if no circles just return the whole image
        # x1 = 0
        # x2 = im.shape[1] - 1
        # y1 = 0
        # y2 = im.shape[0] - 1
        boundingBox = None
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
    # http://docs.scipy.org/doc/scipy-0.16.1/reference/generated/
    #   scipy.ndimage.measurements.find_objects.html
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
            width = blob[1].stop - blob[1].start
            height = blob[0].stop - blob[0].start
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
            x1 = largestblob[1].start
            x2 = largestblob[1].stop
            y1 = largestblob[0].start
            y2 = largestblob[0].stop

    boundingBox = [x1,y1,x2,y2]

    # draw bounding box
    if config.debugImageTitle:
        imbox = drawBoundingBox(im, boundingBox)
        cv2.imwrite(config.debugImageTitle + '_blobboundingbox.jpg', imbox)

    return boundingBox


def findBoundingBox(im, radius):
    "Find bounding box with expected target radius. Returns [x1,y1,x2,y2]"
    # use blob detector if radius<threshold
    if radius < config.blobRadiusMax: # eg 10 pixels
        boundingBox = findBoundingBoxByBlob(im)
    else: # use hough to find circle
        boundingBox = findBoundingBoxByCircle(im, radius)
        # if couldn't find a circle, just use the blob bounding box for approximate answer
        if boundingBox is None:
            boundingBox = findBoundingBoxByBlob(im)
    return boundingBox


if __name__ == "__main__":
    import lib
    orange = '../'+lib.getFilepath('adjust','7206','C2684338','Clear')
    green = '../'+lib.getFilepath('adjust','7206','C2684342','Green')
    blue = '../'+lib.getFilepath('adjust','7206','C2684340','Violet')
    print orange
    channels = [
        ['Orange',orange,0.7,120,-65],
        ['Green',green,1,150,20],
        ['Blue',blue,1,0,0],
        ]
    im = combineChannels(channels)
    show(im)
    cv2.imwrite('foo.jpg',im)


