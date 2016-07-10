
print __doc__

import time

# from PIL import Image

import matplotlib.pyplot as plt
import matplotlib.image as mpim
import matplotlib.patches as patches
import numpy as np


# from scipy.ndimage import measurements, morphology
import scipy.ndimage as ndimage


def drawbox(box):
    "Draw a box on current image"
    x = box[0].start
    y = box[1].start
    width = box[0].stop - x
    height = box[1].stop - y
    plt.gca().add_patch(patches.Rectangle((y,x), height, width, fill=False, edgecolor="green", linewidth=0.5))

def drawboxes(boxes):
    "Draw set of boxes on current image"
    for box in boxes:
        drawbox(box)


# load image
im = mpim.imread('jupiter.png')

# rotate by 180
im = np.rot90(im, 2)

# threshold to binary image
b = 1*(im>0.1)

# label objects
lbl, nobjs = ndimage.measurements.label(b)
# lbl, nobjs = ndimage.measurements.label(im)
print "Number of objects:", nobjs

# get center of mass
# index is 1-based
# x,y = ndimage.measurements.center_of_mass(im1)
# x,y = ndimage.measurements.center_of_mass(b, lbl, 1)
x,y = ndimage.measurements.center_of_mass(im, lbl, 14)
print x,y

# find position of objects
# index is 0-based
blobs = ndimage.find_objects(lbl)
# print blobs
# blob = blobs[13]
# print blob

# draw bounding boxes
# drawboxes(blobs)

def findlargest(blobs):
    widthmax = 0
    heightmax = 0
    for blob in blobs:
        width = blob[0].stop - blob[0].start
        height = blob[1].stop - blob[1].start
        if width>widthmax and height>heightmax:
            widthmax = width
            heightmax = height
            largest = blob
    return largest
    
# find largest object
blob = findlargest(blobs)
print blob

# draw bounding box
# drawbox(blob)


# extract the object (make a copy so doesn't get lost when we zero-out the original image)
obj = np.array(im[blob])

# get background color
bgcolor = obj[0,0]

# zero-out the object location
im[blob] = bgcolor

# paste the object at the center
cx = 400
cy = 400
width = blob[0].stop - blob[0].start
height = blob[1].stop - blob[1].start

# im[400-256/2:400+256/2,400-257/2:400+257/2+1]=j
im[cx-width/2:cx+width/2, cy-height/2:cy+height/2]=obj


# plt.imshow(obj)

# def centerbox(box, cx, cy):
#     im[400-256/2:400+256/2,400-257/2:400+257/2+1]=j


# center image around object





# # show image
plt.gray()
implt = plt.imshow(im)
# # implt = plt.imshow(b)
# # implt = plt.imshow(lbl)



# plot center of mass
# plt.plot([y],[x], 'o')

# draw circle
# plt.Circle((y,x), radius=150)

# save image
# mpim.imsave('test.png', im)

plt.show()







