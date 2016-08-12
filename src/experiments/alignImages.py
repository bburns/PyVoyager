
# align images experiments

import os
import numpy as np
import cv2


import sys; sys.path.append('..') # so can import from main src folder
import config
import libimg




# targetRadius = 100
# targetRadius = 400
targetRadius = 500
imFixed = np.zeros((800,800), np.uint8) #.params
cv2.circle(imFixed, (399,399), targetRadius, 255, -1) # -1=filled

# bbox = [0,750,0,750]
# im = libimg.drawBoundingBox(im, bbox)

# deltax = deltay = 0
# deltax = 100
# deltay = 200
# im = libimg.translateImage(im, deltax, deltay)

# radius = 105
radius = targetRadius+10
x,y=300,300
im = np.zeros((800,800),np.uint8)
# cv2.circle(im,(x,y),radius,255,1)
cv2.circle(im,(x,y),radius,255,-1)

dx,dy,ok = libimg.getImageAlignment(imFixed, im)
print dx,dy,ok

szFixed = imFixed.shape
warp_matrix = np.array([[1,0,dy],[0,1,dx]])
im = cv2.warpAffine(im, warp_matrix, (szFixed[1],szFixed[0]),
                    flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

# same result here
# im = libimg.translateImage(im,-dx,-dy)

libimg.drawCrosshairs(im)



libimg.show(im)

