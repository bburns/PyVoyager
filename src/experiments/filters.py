

import numpy as np
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import libimg



# filename = 'noise/hlines.jpg'
# filename = 'noise/hblock.jpg'
filename = 'noise/hblocks.jpg'

im = cv2.imread(filename, 0)
libimg.show(im)

def getGradientMagnitude(im):
    "Get magnitude of gradient for given image"
    ddepth = cv2.CV_32F
    dx = cv2.Sobel(im, ddepth, 1, 0)
    dy = cv2.Sobel(im, ddepth, 0, 1)
    dxabs = cv2.convertScaleAbs(dx)
    dyabs = cv2.convertScaleAbs(dy)
    mag = cv2.addWeighted(dxabs, 0.5, dyabs, 0.5, 0)
    return mag

mag = getGradientMagnitude(im)
libimg.show(mag)



# threshold to pick out high regions
mask = cv2.adaptiveThreshold(im, maxValue=255,
                             adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                             thresholdType=cv2.THRESH_BINARY_INV,
                             blockSize=3,
                             C=11)
# libimg.show(mask)
# kernel = np.ones((5,1),np.uint8)
kernel = np.ones((5,5),np.uint8)
# kernel = np.ones((3,3),np.uint8)
# mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.dilate(mask, kernel, iterations = 1)


# remove dots from mask
# mask = cv2.medianBlur(mask, 5)
libimg.show(mask)


# maybe do a blob detector and pick out ones with a rectangular shape
# detector = cv2.simpleBlobDetector()
# keypoints = detector.detect(im)
# im = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
# libimg.show(im)


# find contours and bounding boxes, pick out rectangular ones and black the whole rectangle out
# im, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# print contours
# im = cv2.drawContours(im, contours, -1, (0,255,0), 3)
cv2.drawContours(im2, contours, -1, 255, 1)
libimg.show(im2)


# dofindContours, followed by the following code:
maxArea = 0
for contour in contours:
    area = cv2.contourArea(contour)
    if area>10*10:
        x,y,w,h  = cv2.boundingRect(contour)
        # print boundingRect
        # x1,y1=boundingRect[0:2]
        # x2,y2=boundingRect[2:4]
        # cv2.rectangle(im, (x1,y1), (x2,y2), 255, 1)
        # cv2.rectangle(im, (y1,x1), (y2,x2), 255, 1)
        cv2.rectangle(im, (x,y),(x+w,y+h), 0, -1)


    # area = cv2.contourArea(contour)
    # if (area > maxArea):
        # maxArea = area
        # largestContour = contour
# boundingRect = cv2.boundingRect(largestContour)
# print boundingRect
libimg.show(im)




# nowork - looks worse than noise, and edges get corrugated
# black those areas out
# im = im & (255-mask)
# libimg.show(im)

# nowork
# do inpainting in all these regions
# smaller radius = faster, larger = more incursion into bad areas
# im = cv2.inpaint(im, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
# libimg.show(im)







