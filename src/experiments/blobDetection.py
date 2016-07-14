
# experiments with blob detection


# need to have robust algorithm that can handle varying light levels
# simple thresholding doesn't work across all images

# try varying theta, checking the size of the biggest blob,
# and at some point on the graph deciding on the optimal theta value.
# need to do some plots of this for various images and see what kind of curves result

# looks like at the foot of the slope of area would be a good place for theta.


import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.image as mpim # for imread
import scipy.ndimage as ndimage # n-dimensional images - for blob detection

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg



# get path
# folder = 'images/'
folder = '../../test/images/'
# filepath = folder + 'calib.png'
# filepath = folder + 'calib2.png' #.
# filepath = folder + 'ok.png'
# filepath = folder + 'dimsmall.png'
# filepath = folder + 'sharp.png'
# filepath = folder + 'faint.png'
# filepath = folder + 'crescent.png' #.

# filepath = folder + 'saturn.png'
# filepath = folder + 'huge.png'
# filepath = folder + 'limb.png'
# filepath = folder + 'noise.png'
# filepath = folder + 'blank.png'
# filepath = folder + 'edge.png'
# filepath = folder + 'large.png'
# filepath = folder + 'limb2.png'
# filepath = folder + 'point.png'
# filepath = folder + 'blurred.png'
# filepath = folder + 'small.png' #.
# print 'file',filepath

# so having probs with faint images and small ones
# the crescent could be found by hough, but how would you know you needed it? 

# *maybe we should be using hough with a high acc th,
# so we'd be sure of having a circle
# if no circle found, use the blob test

# thdiff = -0.02
# thdiff = -0.05
# thdiff = -0.5
# thdiff = -0.015
# thdiff = -0.0125
thdiff = config.blobAreaDerivativeMax


results = lib.readCsv('images/_files.csv')
fileids = results.keys()
fileids.sort()
for fileid in fileids:
    
    filename = fileid + '.png'
    filepath = folder + filename
    im = mpim.imread(filepath) # values are 0.0-1.0
    outpath = folder + 'out/' + filename
    
    # libimg.show(im)
    # stretch
    im = cv2.normalize(im, None, 0, 1.0, cv2.NORM_MINMAX)

    # print im.min(), im.max()  # 0.0, 0.5294
    # # stretch the histogram - works
    # im2 = libimg.mpim2cv2(im)
    # equ = cv2.equalizeHist(im2)
    # im = libimg.cv22mpim(equ)
    # res = np.hstack((im2,equ)) #stacking images side-by-side
    # # cv2.imwrite('res.png',res)
    # libimg.show(res)
    # end

    # adaptive thresholding
    # put into findboundingboxbyblob2


    # # show binarized image with bounding box
    # config.debugImages = True
    # th = 0.13
    # boundingBox = libimg.findBoundingBoxByBlob(im, th)

    # show image with best bounding box
    config.debugImages = False
    boundingBox = libimg.findBoundingBoxByBlob2(im, thdiff)
    im2 = libimg.mpim2cv2(im)
    im2 = libimg.gray2rgb(im2)
    libimg.drawBoundingBox(im2, boundingBox)
    # libimg.show(im2)
    cv2.imwrite(outpath, im2)




def plotAreaByThreshold(im, thdiff):
    
    config.debugImages = False
    
    thmin = 0.02
    thmax = 0.25
    thstep = 0.01
    imax = int((thmax-thmin)/thstep)+1

    # lastarea = 1
    lastarea = 0
    maxarea = 800*800.0
    maxderiv = 1/thstep
    ths = []
    areas = []
    derivs = []
    # thdiff = -0.05
    thbest = 0
    areabest = 0
    boundingBoxBest = [0,0,799,799]
    for i in range(0,imax):
        th = thmin + i * thstep
        ths.append(th)
        boundingBox = libimg.findBoundingBoxByBlob(im, th)
        x1,y1,x2,y2 = boundingBox
        area = (x2-x1)*(y2-y1) / maxarea # area = 0 to 1
        area = math.log(area) # area goes from 1 to 0, so this should go from 0 to -infinity
        deriv = (area - lastarea) / thstep / maxderiv
        # deriv = (math.log(area) - math.log(lastarea)) / thstep / maxderiv
        # logarea = math.log(area)
        print i, th, area, deriv
        areas.append(area)
        derivs.append(deriv)
        # if deriv<thdiff and deriv<0:
        if deriv<thdiff:
            thbest = th
            areabest = area
            boundingBoxBest = boundingBox
        lastarea = area

    # derivs = np.diff(areas)
    print thbest
    print areabest
    print boundingBoxBest

    plt.plot(ths, areas) # blue
    plt.plot(ths, derivs) # green
    plt.axvline(thbest)
    plt.show()
    
    return thbest

# show plot of logarea and derivative vs threshold
# thbest = plotAreaByThreshold(im, thdiff)
# config.debugImages = True
# boundingBox = libimg.findBoundingBoxByBlob(im, thbest)



# show binarized image with bounding box
# thbest = 0.16
# for thbest in [0.02,0.04,0.06,0.08,0.10,0.12,0.14,0.16]: #,0.18,0.20,0.22,0.24,0.26,0.28,0.30]:
    # config.debugImages = True
    # boundingBox = libimg.findBoundingBoxByBlob(im, thbest)




# th = thbest
# # libimg.showMpim(im)
# # th = 0.07 # half white
# # th = 0.1 # still way too much white
# # th = 0.12 # some white, but might work
# # th = 0.14 # perfect
# # th = 0.16 # great
# # th = 0.18 # good
# # th = 0.2 # good
# # th = 0.22 # good
# # th = 0.25 # still there
# # th = 0.5 # too small
# b = 1*(im>th) # threshold to binary image
# libimg.showMpim(b)

# # def bw2rgb(im):
# #     w, h = im.shape
# #     # ret = np.empty((w, h, 3), dtype=np.uint8)
# #     ret = np.empty((w, h, 3), dtype=np.float)
# #     ret[:, :, 2] =  ret[:, :, 1] =  ret[:, :, 0] =  im
# #     return ret



# show cropped image
# x1,y1,x2,y2 = boundingBox
# imcrop = im[x1:x2,y1:y2]
# libimg.showMpim(imcrop)



# # mpim blob detection - works, as in vgBuildCenters with RAW images
# im = mpim.imread(filepath) # values are 0.0-1.0
# # print im
# # im2 = libimg.mpim2cv2(im)
# # libimg.show(im2)
# # show thresholded image
# th = 0.2
# b = 1*(im>th) # threshold to binary image
# libimg.showMpim(b)
# # find blobs
# lbl, nobjs = ndimage.measurements.label(b) # label objects
# blobs = ndimage.find_objects(lbl)
# print blobs
# # well it does something anyway


# # cv2 blob detection - works, but size of blob doesn't match image
# im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE) # values are 0-255
# # im = cv2.imread(filepath) # values are 0-255
# # im = 255-im
# print im
# libimg.show(im)
# # # nowork
# # detector = cv2.SimpleBlobDetector()
# # keypoints = detector.detect(im)
# # print keypoints
# # make mask
# # mask = cv2.inRange(im, 20,255) # create binary mask - values are 0 or 255
# # print mask
# # libimg.show(mask)
# # nowork
# # contours, _ = cv2.findContours(im, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# # for c in contours:
# #     rect = cv2.boundingRect(c)
# #     if rect[2] < 5 or rect[3] < 5: continue
# #     # print cv2.contourArea(c)
# #     print rect
# #     color = (255,0,0)
# #     cv2.rectangle(im, rect[:2], rect[2:4], color, 2)    
# # libimg.show(im)
# # find blobs
# # blobDetector = libimg.getBlobDetector()
# blobDetector = libimg.getBlobDetector(10,200)
# keypoints = blobDetector.detect(im)
# print 'keypoints',keypoints
# maxsize = 0
# bestKeypoint = None
# for keypoint in keypoints:
#     # print keypoint
#     print keypoint.pt
#     print keypoint.size
#     print
#     if keypoint.size>maxsize:
#         maxsize=keypoint.size
#         bestKeypoint=keypoint
# color = (0,0,255) # red
# # if len(keypoints)>0:
# # # draw blobs as circles
# #     # last flag ensures the size of the circle corresponds to the size of blob
# #     im2 = cv2.drawKeypoints(im, keypoints, np.array([]), color, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
# #     libimg.show(im2)
# keypoints = [bestKeypoint]    
# im2 = cv2.drawKeypoints(im, keypoints, np.array([]), color, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
# libimg.show(im2)



print 'done'

