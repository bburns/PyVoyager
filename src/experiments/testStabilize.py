
# refinement of feature alignment experiments



# inprogress



import matplotlib.pyplot as plt
import matplotlib.image as mpim
import numpy as np
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg



folder = 'alignments/'
outputfolder = folder + 'output/'

files = [
    # these are the first ones to go wrong in 5101
    # works fine here - found/fixed bug
    # 'C1462321_centered_Clear',
    # 'C1462323_centered_Clear',

    # 'C1462341_centered_Violet',
    # 'C1462343_centered_Blue',

    # 'C1467552_centered_Uv',
    # 'C1467554_centered_Blue',
    # 'C1467556_centered_Green',
    # 'C1467558_centered_Orange',
    # 'C1467821_centered_Uv',
    # 'C1467823_centered_Blue',
    # 'C1467825_centered_Green',

    # the middle one is offset from the other two by 20+ pixels
    'C1540122_centered_Blue',
    'C1540124_centered_Orange',
    'C1540126_centered_Green',

    # 'C2447705_centered_Green',
    # 'C2447711_centered_Ch4_U',
    # 'C2448604_centered_Violet',
    # 'C2448610_centered_Blue',
    # 'C2448702_centered_Violet',
    # 'C2448726_centered_Green',
    ]


lastFilename = files[0] + '.jpg'
# write first file to start off
im1 = cv2.imread(folder + lastFilename)
newFilename = outputfolder + lastFilename
cv2.imwrite(newFilename, im1)

for filename in files:
    filename = filename + '.jpg'
    if filename==lastFilename: continue

    print lastFilename, filename

    infile = outputfolder + lastFilename
    # outfile = o
    x,y,radius,stabilizationOk = centerAndStabilizeImageFile(infile, outfile, fixedfile, lastRadius)

    im1 = cv2.imread(outputfolder + lastFilename)
    im2 = cv2.imread(folder + filename)
    im1_gray = cv2.cvtColor(im1,cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2,cv2.COLOR_BGR2GRAY)
    sz = im1.shape
    warp_mode = cv2.MOTION_TRANSLATION
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    number_of_iterations = 5000
    termination_eps = 1e-10
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                number_of_iterations,  termination_eps)
    # Run the ECC algorithm. The results are stored in warp_matrix.
    try:
        (cc, warp_matrix) = cv2.findTransformECC (im1_gray, im2_gray, warp_matrix,
                                                  warp_mode, criteria)
    except:
        print 'fail!'
    else:
        print warp_matrix
        # [[ 1.          0.          0.0037005 ]
        #  [ 0.          1.          0.00485788]]
        # ? are these fractions of 800? (* 800 0.0037005) 2.96, (* 800 0.00485788) 3.88 maybe so
        im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]),
                                     flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
        # Show final results
        # cv2.imshow("Image 1", im1)
        # cv2.imshow("Image 2", im2)
        # cv2.imshow("Aligned Image 2", im2_aligned)
        # cv2.waitKey(0)
        newFilename = outputfolder + filename # [:-4] + '_new.jpg'
        print newFilename
        cv2.imwrite(newFilename, im2_aligned)
    finally:
        lastFilename = filename
