
# align images experiments

import os
import numpy as np
import cv2


import sys; sys.path.append('..') # so can import from main src folder
import config
import libimg
import lib


# ECC Maximization
# ----------------------------------------

if 1:
# if 0:
    # ganymede - works
    folder = '../../data/step04_adjust/VGISS_5117/'
    file1 = folder + 'C1640236_adjusted_Blue.jpg'
    file2 = folder + 'C1640234_adjusted_Violet.jpg'
    file3 = folder + 'C1640238_adjusted_Orange.jpg'

    # ganymede - works
    # folder = '../../data/step04_adjust/VGISS_5117/'
    # file1 = folder + 'C1640256_adjusted_Blue.jpg'
    # file2 = folder + 'C1640300_adjusted_Green.jpg'
    # file3 = folder + 'C1640258_adjusted_Orange.jpg'

    # clouds - eh, but looks nice
    # folder = '../../data/step04_adjust/VGISS_5116/'
    # file1 = folder + 'C1635023_adjusted_Violet.jpg'
    # file2 = ''
    # file3 = folder + 'C1635021_adjusted_Orange.jpg'

    # jupiter and moons - works
    # folder = '../../data/step04_adjust/VGISS_5112/'
    # file1 = folder + 'C1610017_adjusted_Violet.jpg'
    # file2 = ''
    # file3 = folder + 'C1610015_adjusted_Orange.jpg'


    im1 = cv2.imread(file1,0)
    if file2:
        im2 = cv2.imread(file2,0)
    else:
        im2 = np.zeros((800,800),np.uint8)
    im3 = cv2.imread(file3,0)
    assert not im1 is None
    assert not im2 is None
    assert not im3 is None

    # align im2 to im1
    dx,dy,ok = libimg.getImageAlignment(im1, im2)
    print dx,dy,ok
    if ok:
        warp_matrix = np.array([[1,0,dy],[0,1,float(dx)]]) # eh use float to set the matrix type
        im2 = cv2.warpAffine(im2, warp_matrix, im1.shape[:2],
                            flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        # libimg.show(im2)

    # align im3 to im1
    dx,dy,ok = libimg.getImageAlignment(im1, im3)
    # dx,dy,ok = libimg.getImageAlignment(im2, im3)
    print dx,dy,ok
    if ok:
        warp_matrix = np.array([[1,0,dy],[0,1,float(dx)]]) # eh use float to set the matrix type
        im3 = cv2.warpAffine(im3, warp_matrix, im1.shape[:2],
                            flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

    # merge channels
    im = cv2.merge((im1,im2,im3)) # b,g,r
    libimg.show(im)
    cv2.imwrite('merged.jpg',im)


# if 1:
if 0:

    # draw a disc
    targetRadius = 100
    # targetRadius = 400
    # targetRadius = 500
    imFixed = np.zeros((800,800), np.uint8) #.params
    cv2.circle(imFixed, (399,399), targetRadius, 255, -1) # -1=filled

    # bbox = [0,750,0,750]
    # im = libimg.drawBoundingBox(im, bbox)

    # deltax = deltay = 0
    # deltax = 100
    # deltay = 200
    # im = libimg.translateImage(im, deltax, deltay)

    # draw another disc, offset from center
    # radius = 105
    radius = targetRadius+10
    x,y=300,300
    im = np.zeros((800,800),np.uint8)
    # cv2.circle(im,(x,y),radius,255,1)
    cv2.circle(im,(x,y),radius,255,-1)

    # align them
    dx,dy,ok = libimg.getImageAlignment(imFixed, im)
    print dx,dy,ok

    # shift second one
    szFixed = imFixed.shape
    warp_matrix = np.array([[1,0,dy],[0,1,float(dx)]]) # eh use float to set the matrix type
    im = cv2.warpAffine(im, warp_matrix, (szFixed[1],szFixed[0]),
                        flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

    # same result here
    # im = libimg.translateImage(im,-dx,-dy)

    libimg.drawCrosshairs(im)

    libimg.show(im)

# Feature alignment
# ----------------------------------------


