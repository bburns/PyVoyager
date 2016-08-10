
# inpainting experiments


import numpy as np
import cv2


import sys; sys.path.append('..') # so can import from main src folder
import config
import libimg



# filename = 'noise/hlines.jpg'
filename = 'noise/hblock.jpg'


# read image
# ----------------------------------------
im = cv2.imread(filename, 0)
libimg.show(im)



# try smoothing the image with a vertical kernel
# ----------------------------------------
# kernel = np.ones((3,1),np.float32)/2
# kernel[1,0]=0
# im = cv2.filter2D(im,-1,kernel)
# libimg.show(im)
# stop



# create mask locating the 'scratches' to be removed
# ----------------------------------------


# mask = im


# just want one pixel high white lines


# threshold
# this works great for emphasizing the sharp regions
# mask = cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 6)
mask = cv2.adaptiveThreshold(im, maxValue=255,
                             adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                             thresholdType=cv2.THRESH_BINARY_INV,
                             blockSize=3,
                             C=5)
# libimg.show(mask)


# morphological operations
# kernel = np.ones((3,1),np.uint8)
kernel = np.ones((5,1),np.uint8)
# kernel = np.ones((3,3),np.uint8)
# mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.dilate(mask, kernel, iterations = 1)
# libimg.show(mask)
# cv2.imwrite('noise/hlines_mask.jpg', mask)


# apply salt and pepper filter to mask
# this actually works great for removing thin lines
# try on other noise
mask = cv2.medianBlur(mask, 5)
libimg.show(mask)


imblurred = cv2.medianBlur(im, 5)

imnet = im + ((imblurred - im) & mask)
libimg.show(imnet)


# im[mask==0] = 0
# libimg.show(im)
# im = cv2.medianBlur(im, 5)
# libimg.show(im)

# mask = cv2.blur(mask, (5,5))
# libimg.show(mask)





# ret, mask = cv2.threshold(im, 25, 255, cv2.THRESH_BINARY)
# libimg.show(mask)


# bilateral filter preserves edges (which is actually not what we want)
# ksize = 5
# mask = cv2.bilateralFilter(im, ksize, ksize*2, ksize/2);
# libimg.show(mask)




# remove the 'scratches' by inpainting
# ----------------------------------------
# im = cv2.inpaint(im, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
# libimg.show(im)
# cv2.imwrite('noise/hlines_result.jpg',im)



# old


# erosion = cv2.erode(mask, kernel, iterations = 1)
# dilation = cv2.dilate(mask, kernel, iterations = 1)
# libimg.show(dilation)
# mask=dilation
# opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
# erosion = 255-erosion
# libimg.show(erosion)



