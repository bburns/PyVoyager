
# continuation of feature alignment experiments

import matplotlib.pyplot as plt
import matplotlib.image as mpim
# import matplotlib.patches as patches
import numpy as np
# import scipy.ndimage as ndimage
# import scipy.misc as misc
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg



folder = 'alignments/'

files = [
    'C2447705_centered_Green.jpg',
    'C2447711_centered_Ch4_U.jpg',
    'C2448604_centered_Violet.jpg',
    'C2448610_centered_Blue.jpg',
    'C2448702_centered_Violet.jpg',
    'C2448726_centered_Green.jpg',
    ]


lastFilename = folder + files[0]
for filename in files:
    filename = folder + filename
    if filename==lastFilename: continue

    print lastFilename, filename

    im1 = cv2.imread(lastFilename)
    im2 = cv2.imread(filename)
    im1_gray = cv2.cvtColor(im1,cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY)
    sz = im1.shape
    warp_mode = cv2.MOTION_TRANSLATION

    warp_matrix = np.eye(2, 3, dtype=np.float32)
    number_of_iterations = 5000
    termination_eps = 1e-10
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)
    # Run the ECC algorithm. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC (im1_gray,im2_gray,warp_matrix, warp_mode, criteria)
    print warp_matrix
    # [[ 1.          0.          0.0037005 ]
    #  [ 0.          1.          0.00485788]]
    # ? are these fractions of 800? (* 800 0.0037005) 2.96, (* 800 0.00485788) 3.88 maybe so
    im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
    # Show final results
    # cv2.imshow("Image 1", im1)
    # cv2.imshow("Image 2", im2)
    # cv2.imshow("Aligned Image 2", im2_aligned)
    # cv2.waitKey(0)
    newFilename = filename[:-4] + '_new.jpg'
    cv2.imwrite(newFilename, im2_aligned)

    lastFilename = filename
