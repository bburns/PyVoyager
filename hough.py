

import cv2


import matplotlib.pyplot as plt
import matplotlib.image as mpim
# import matplotlib.patches as patches
import numpy as np
# import scipy.ndimage as ndimage
# import scipy.misc as misc

import cv2


import config
import lib
import libimg


testfile = 'a.png'
infile = config.test_folder + testfile

# read image
im = mpim.imread(infile) # load image

# process
if config.rotate_image:
    im = np.rot90(im, 2) # rotate by 180

    
im2 = cv2.imread(infile)
output = im2.copy()
gray = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY)

dp = 1.2
minDist = 100
param1=None
param2=None
minRadius=None
maxRadius=None
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, minDist, param1, param2, minRadius, maxRadius)
if circles is not None:
    circles = np.round(circles[0,:]).astype('int')
    for (x,y,r) in circles:
        cv2.circle(output, (x,y), r, (0,255,0), 4)
        # cv2.rectangle
    cv2.imshow("output", np.hstack([image, output]))
    
# plt.imshow(im)
# b = 1*(im>epsilon)
# x1,x2,y1,y2=v.find_object_edges(b,0,0)
# x1,x2,y1,y2=v.find_object_edges(im,0,0)
# v.drawbox(x1,x2,y1,y2)
# plt.imshow(b)
plt.imshow(im)
plt.show()
# mpim.imsave(b, 'b.png')


# axis=0 # x-axis
# # axis=1 # y-axis
# N=5 # running average to smooth plot
# epsilon=0.2 # threshold 

# sums = np.sum(im, axis=axis)
# diff = np.diff(sums)
# diffsq = np.square(diff)
# diffsqln = np.log(diffsq)
# smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
# k = 1*(smoothed>epsilon)
# # icenter = v.find_center_1d(smoothed, 0)


# # show image
# # plt.plot(k)
# # plt.show()


# # show diffs

# plt.figure(1)

# plt.subplot(4,1,1)
# plt.plot(diffsq)

# plt.subplot(4,1,2)
# plt.plot(diffsqln)

# plt.subplot(4,1,3)
# plt.plot(smoothed)
# plt.axhline(epsilon)

# plt.subplot(4,1,4)
# plt.plot(k)

# plt.show()


# # old
# # imcrop = v.center_image(im, True)
# # imcrop[399, 0:799] = 0.2
# # imcrop[0:799, 399] = 0.2


# # save image
# # outfile = args.prefix + infile
# # misc.imsave(outfile, imcrop)




print 'done'



