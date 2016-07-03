

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


# testfile = 'a.png'
# testfile = 'b.png'
# testfile = 'c.png'
testfile = 'd.png'
infile = config.test_folder + testfile


#     im = np.rot90(im, 2) # rotate by 180

    
im = cv2.imread(infile)

# rotate 180deg
# im = cv2.imread(infile, 0) # ,0=bw?
# rows, cols = im.shape
# M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
# im = cv2.warpAffine(im, M, (cols, rows))

output = im.copy()
gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

dp = 1.2
minDist = 1000
param1=0.1
param2=200
minRadius=10
maxRadius=100
circles = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT, dp, minDist, param1, param2, minRadius, maxRadius)
if circles is not None:
    circles = np.round(circles[0,:]).astype('int')
    # for (x,y,r) in circles:
        # cv2.circle(output, (x,y), r, (0,255,0), 4)
    circle = circles[0]
    (x,y,r) = circle
    cv2.circle(output, (x,y), r, (0,255,0), 4)
    cv2.imshow("output", np.hstack([im, output]))
    cv2.waitKey(0)
    # return circle # (x,y,r)
else:
    print 'no circles'
    # return None
    
# plt.imshow(im)
# plt.show()
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



