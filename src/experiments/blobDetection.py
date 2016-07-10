
# experiments with blob detection

# need to have robust algorithm that can handle varying light levels
# simple thresholding won't work across all images

# something about varying theta,
# checking the size of the biggest blob,
# and at some point on the graph deciding on the optimal theta value.

# need to do some plots of this for various images and see what kind of curves result

import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg

import matplotlib.image as mpim # for imread
import scipy.ndimage as ndimage # n-dimensional images - for blob detection


# get path
folder = 'blobDetection/'
# filepath = folder + 'ok.png'
filepath = folder + 'dim.png'
# filepath = folder + 'huge.png'
# filepath = folder + 'limb.png'
# filepath = folder + 'saturn.png'
# filepath = folder + 'sharp.png'
# filepath = folder + 'noise.png'
print 'file',filepath


# iterate over some threshold values,
# plot max blobsize vs threshold

im = mpim.imread(filepath) # values are 0.0-1.0





# print im.min(), im.max()  # 0.0, 0.5294
# # stretch the histogram - works
# im2 = libimg.mpim2cv2(im)
# equ = cv2.equalizeHist(im2)
# res = np.hstack((im2,equ)) #stacking images side-by-side
# # cv2.imwrite('res.png',res)
# libimg.show(res)
# end





# thmin = 0.05
# thmax = 0.20
# thstep = 0.01
# imax = int((thmax-thmin)/thstep)+1
# print imax

# ths = []
# areas = []
# # logareas = []
# derivs = []
# lastarea = 1
# maxarea = 800*800.0
# maxderiv = 1/thstep
# thdiff = -0.9
# # derivmin = -1
# # derivmax = -0.9
# thbest = 0
# areabest = 0
# boundingBoxBest = []
# for i in range(0,imax):
#     th = thmin + i * thstep
#     ths.append(th)
#     boundingBox = libimg.findBoundingBoxByBlob(im, th)
#     x1,y1,x2,y2 = boundingBox
#     area = (x2-x1)*(y2-y1) / maxarea # area = 0 to 1
#     # logarea = math.log(area)
#     deriv = (area - lastarea) / thstep / maxderiv
#     print i, th, area, deriv
#     areas.append(area)
#     # logareas.append(logarea)
#     derivs.append(deriv)
#     if deriv>thdiff:
#         thbest = th
#         areabest = area
#         boundingBoxBest = boundingBox
#     # if deriv>=derivmin and deriv<=derivmax:
#         # thbest = th
#         # break
#     # print i, th, area, logarea, deriv


# print thbest
# print areabest
# print boundingBoxBest

# plt.plot(ths, areas)
# # plt.plot(ths, logareas)
# plt.plot(ths, derivs)
# plt.show()



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


boundingBox = libimg.findBoundingBoxByBlob2(im)
# # im = [im,im,im]
# # im = bw2rgb(im)
# # im = libimg.mpim2cv2(im)
# # im = cv2.cvtColor(im,cv2.COLOR_GRAY2RGB)
im2 = libimg.drawBoundingBox(im, boundingBox)
libimg.showMpim(im2)


x1,y1,x2,y2 = boundingBox
# imcrop = im[y1:y2,x1:x2]
imcrop = im[x1:x2,y1:y2]
libimg.showMpim(imcrop)






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

