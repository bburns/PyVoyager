

import numpy as np
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import libimg



# filename = 'noise/hline_top.jpg'

# filename = '../../data/step04_adjusted/v0.43/VGISS_5117/C1640000_adjusted_Orange.jpg'
# filename = '../../data/step03_images/VGISS_5117/C1640000_CALIB_ORANGE.png'
filename = '../../data/step03_images/VGISS_5117/C1640202_CALIB_CLEAR.png'
# C1640314_adjusted_Violet

im = cv2.imread(filename, 0)
libimg.show(im)

# im = 20*im
# libimg.show(im)


im = libimg.stretchHistogram(im)
libimg.show(im)








