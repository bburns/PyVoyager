
# experiments with histograms


import numpy as np
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import libimg



# filename = '../../data/step03_images/VGISS_5117/C1640000_CALIB_ORANGE.png'
filename = '../../data/step04_adjustments/v0.43/VGISS_5117/C1640000_adjusted_Orange.jpg'

# im = cv2.imread(filename, 0 | cv2.LOAD_IMAGE_ANYDEPTH)
im = cv2.imread(filename, 0 | cv2.IMREAD_ANYDEPTH)
# im = cv2.imread(filename, 2)
libimg.show(im)

print type(im[0][0])

# convert image to 8 bit
if type(im[0][0])==np.uint16:
    im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX) # black
    im = np.array(im, np.uint8) # noisy
    libimg.show(im)



im = libimg.stretchHistogram(im)
libimg.show(im)



# if 1:
#     a=np.array([1,2,3,4,5,1,5],np.uint8)
#     print 'a',a

#     mask = None # lets you filter to part of an image
#     histSize = [6] # number of bins
#     ranges = [0, 6] # range of intensity values
#     hist = cv2.calcHist([a], [0], None, histSize, ranges)
#     print 'hist',[int(x) for x in hist]

#     # ignore top n%, or top n pixels
#     # start at top, get cumulative sum downwards until reach certain amount of pixels
#     npixels = len(a)
#     npixelsTop = 3
#     sum = 0
#     maxvalue = 5
#     for i in xrange(5,0,-1):
#         sum += hist[i]
#         if sum>npixelsTop:
#             maxvalue = i
#             break
#     print 'maxvalue',maxvalue

#     # set values > maxvalue to maxvalue
#     # see http://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html
#     # np.clip(im, 0, maxvalue, im)
#     np.clip(a, 0, maxvalue, a)
#     # show(im)
#     print 'a, clipped',a

#     # stretch image values
#     # im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
#     a = cv2.normalize(a, None, 0, 30, cv2.NORM_MINMAX)
#     print 'a, normalized\n',a
#     # show(im)








