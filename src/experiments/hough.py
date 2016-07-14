
# tests of hough circle detection


import matplotlib.pyplot as plt
import matplotlib.image as mpim
# import matplotlib.patches as patches
import numpy as np
# import scipy.ndimage as ndimage
# import scipy.misc as misc
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg


# constants
red = (0,0,255)
green = (0,255,0)

# get path
folder = '../../test/images/'
# filepath = folder + 'blurred.png'
filepath = folder + 'crescentsmall.png'
print 'file',filepath



config.drawBlob = True
config.drawCircle = True
config.drawCircles = True
config.drawCrosshairs = True



# load image
im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE) # values are 0-255
# im = mpim.imread(filepath) # values are 0-1

# yuck
# im = cv2.equalizeHist(im)

# stretch
im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)


# thdiff = -0.025
# thdiff = -0.0125
# bbox = libimg.findBoundingBoxByHoughThenBlob(im, thdiff)
bbox = libimg.findBoundingBoxByBlobThenHough(im)
# im = libimg.gray2rgb(im)
# libimg.drawBoundingBox(im, bbox)
libimg.show(im)

# # show canny edge detection, which is what hough works with
upper = 200
lower = upper/2
im2 = cv2.Canny(im, lower, upper)
libimg.show(im2)


# # find best circle
# circle = libimg.findCircle(im) # (x,y,r)
# if type(circle) != type(None): #. gives warning
#     im = libimg.gray2rgb(im)
#     libimg.drawCircle(im, circle)
#     libimg.show(im)



# # find circles
# # works
# circles = libimg.findCircles(im)
# print 'circles found:',len(circles)
# im = libimg.gray2rgb(im)
# i = 0
# for circle in circles: # circle = (x,y,r)
#     if i==0:
#         libimg.drawCircle(im, circle, red)
#         # break
#     else:
#         libimg.drawCircle(im, circle, green)
#     i += 1
# libimg.show(im)


# # combined algos
# im = mpim.imread(infile)
# bbox = findBoundingBox(im)

# im = cv2.imread(infile)
# im = np.rot90(im, 2) # rotate by 180 #.nowork

# plt.imshow(im)
# plt.show()
# mpim.imsave(b, 'b.png')

# axis=0 # x-axis
# # axis=1 # y-axis
# N=5 # running average to smooth plot
# epsilon=0.2 # threshold 

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



