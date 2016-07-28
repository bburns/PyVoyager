

# blob detection using Laplacian of Gaussian (LoG)



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




folder = 'alignments/'

file1 = folder + 'C2448604_centered_Violet.jpg'
file2 = folder + 'C2448610_centered_Blue.jpg'


img = cv2.imread(file2) # values are 0-255
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
gray = np.float32(gray)







