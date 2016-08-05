

# blob detection with adaptive thresholding


import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.image as mpim # for imread
import scipy.ndimage as ndimage # n-dimensional images - for blob detection

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg


folder = '../../test/images/'


filename = 'C2580729_ariel_point.jpg'
filepath = folder + filename

im = cv2.imread(filepath)

im = libimg.resizeImage(im, 600,600)
# libimg.show(im)

im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
libimg.show(im)

# b = cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)
b = cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 6)
libimg.show(b)

# print im

# th=3
# b = 255*(im>th)
# libimg.show(b)





