

import numpy as np
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import libimg



# filename = 'noise/hlines.jpg'
# filename = 'noise/hblock.jpg'
filename = 'noise/hblock2.jpg'
# filename = 'noise/hblocks.jpg'

im = cv2.imread(filename, 0)
libimg.show(im)


# if 1:
if 0:
    mag = libimg.getGradientMagnitude(im)
    libimg.show(mag,'gradiant mag')


if True:
# if False:

    # threshold to pick out high regions
    # mask = cv2.adaptiveThreshold(mag, maxValue=255,
    mask = cv2.adaptiveThreshold(im, maxValue=255,
                                 adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 thresholdType=cv2.THRESH_BINARY_INV,
                                 blockSize=3,
                                 # C=11)
                                 C=9)
    libimg.show(mask,'mask')

    kernel = np.ones((1,21), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # dilate then erode
    libimg.show(mask,'mask closed')

    # mask = cv2.dilate(mask, kernel, iterations = 1)

    kernel = np.ones((1,2), np.uint8)
    mask = cv2.erode(mask, kernel, iterations = 1)
    libimg.show(mask,'mask erode')

    # mask = cv2.medianBlur(mask, 3)

    # find contours
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(im2, contours, -1, 255, 1)
    # libimg.show(im2,'contours')

    # find bounding boxes, pick out rectangular ones and black whole rectangle out
    for contour in contours:
        # area = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        if w>100 and w>h*3:
            cv2.rectangle(im, (x,y), (x+w,y+h), 0, -1) # filled black rectangle
    libimg.show(im, 'blacked out')


    # nowork - looks worse than noise, and edges get corrugated
    # black those areas out
    # im = im & (255-mask)
    # libimg.show(im)

    # nowork
    # do inpainting in all these regions
    # smaller radius = faster, larger = more incursion into bad areas
    # im = cv2.inpaint(im, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    # libimg.show(im)


if True:
# if 0:

    # try removing noise near sharp edges (median blur)
    # the larger C is, the less noise will be removed

    # make a mask at high gradient areas
    mask = cv2.adaptiveThreshold(im, maxValue=255,
                                 adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 thresholdType=cv2.THRESH_BINARY_INV,
                                 blockSize=3,
                                 # C=2) # ends up blurring triton
                                 C=4) # good compromise
                                 # C=5) # leaves too much noise
    libimg.show(mask,'mask1')

    # expand mask
    kernel = np.ones((3,1), np.uint8)
    # kernel = np.ones((5,1), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1) # expand edge mask
    mask = cv2.medianBlur(mask, 5) # remove dots from mask
    libimg.show(mask,'mask')

    # remove noise from image
    # imblurred = cv2.medianBlur(im, 5)
    imblurred = cv2.medianBlur(im, 3)

    # combine image with blurred version
    im = im + ((imblurred - im) & mask)

    libimg.show(im,'medianblur at high gradient areas')




    # nowork - cv2's blob detector looks for circular blobs
    # maybe do a blob detector and pick out ones with a rectangular shape
    # detector = cv2.simpleBlobDetector()
    # keypoints = detector.detect(im)
    # im = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # libimg.show(im)

    # im, contours,kk hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel) # erode then dilate
