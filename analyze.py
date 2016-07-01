
# analyze an image
# testbed for bounding box detection
# --------------------------------------------------------------------------------

# algorithm:
# walk over columns
# get sum along entire column
# get the difference between adjacent columns
# square the difference to get absolute value
# take the log to bring out the details
# threshold at epsilon
# find the first value>0 from left and right directions


import matplotlib.pyplot as plt
import matplotlib.image as mpim
import matplotlib.patches as patches
import numpy as np
import scipy.ndimage as ndimage
import scipy.misc as misc

import sys
sys.path.append('pyvoyager')
import config
import lib
import libimg



# testfile = 'a.png'
# testfile = 'a8x8.png'
testfile = 'b.png'
infile = config.test_folder + testfile


# read image

im = mpim.imread(infile) # load image

if config.rotate_image:
    im = np.rot90(im, 2) # rotate by 180

# process
# im = np.rot90(im, 2) # rotate by 180
# plt.imshow(im)
# b = 1*(im>epsilon)
# x1,x2,y1,y2=v.find_object_edges(b,0,0)
# x1,x2,y1,y2=v.find_object_edges(im,0,0)
# v.drawbox(x1,x2,y1,y2)
# plt.imshow(b)
# plt.imshow(im)
# plt.show()
# mpim.imsave(b, 'b.png')


axis=0 # x-axis
# axis=1 # y-axis
N=5 # running average to smooth plot
epsilon=0.2 # threshold 

sums = np.sum(im, axis=axis)
diff = np.diff(sums)
diffsq = np.square(diff)
diffsqln = np.log(diffsq)
smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
k = 1*(smoothed>epsilon)
# icenter = v.find_center_1d(smoothed, 0)


# show image
# plt.plot(k)
# plt.show()


# show diffs

plt.figure(1)

plt.subplot(4,1,1)
plt.plot(diffsq)

plt.subplot(4,1,2)
plt.plot(diffsqln)

plt.subplot(4,1,3)
plt.plot(smoothed)
plt.axhline(epsilon)

plt.subplot(4,1,4)
plt.plot(k)

plt.show()


# old
# imcrop = v.center_image(im, True)
# imcrop[399, 0:799] = 0.2
# imcrop[0:799, 399] = 0.2


# save image
# outfile = args.prefix + infile
# misc.imsave(outfile, imcrop)

