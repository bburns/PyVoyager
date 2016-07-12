

# try doing canny then blob detection



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




folder = 'images/'
# filepath = folder + 'calibokayish.png'
# filepath = folder + 'calibblurred.png' #.
# filepath = folder + 'calibfaint.png'
# filepath = folder + 'calibdim.png'

# filepath = folder + 'ok.png'
# filepath = folder + 'dimsmall.png'
# filepath = folder + 'sharp.png'
# filepath = folder + 'crescent.png' #.

# filepath = folder + 'saturn.png'
# filepath = folder + 'huge.png'
# filepath = folder + 'limb.png'
# filepath = folder + 'noise.png'
# filepath = folder + 'blank.png'
# filepath = folder + 'edge.png'
# filepath = folder + 'large.png'
# filepath = folder + 'limb2.png'
# filepath = folder + 'point.png'
# filepath = folder + 'blurred.png'
# filepath = folder + 'small.png' #.
# print 'file',filepath


# im = cv2.imread(filepath) # values are 0-255
# im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
# libimg.show(im)
# upper = 200
# lower = upper/2
# im = cv2.Canny(im, lower, upper)
# libimg.show(im)


results = lib.readCsv('images/_files.csv')
fileids = results.keys()
fileids.sort()
for fileid in fileids:
    
    filename = fileid + '.png'
    filepath = folder + filename
    print filepath
    # im = mpim.imread(filepath) # values are 0.0-1.0
    im = cv2.imread(filepath)
    outpath = folder + 'out/' + filename
    
    # im = cv2.imread(filepath) # values are 0-255
    im = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX)
    # libimg.show(im)
    upper = 200
    lower = upper/2
    im = cv2.Canny(im, lower, upper)
    
    # dilate the edges
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2))
    # im = np.zeros((100,100), dtype=np.uint8)
    # im[50:,50:] = 255
    im = cv2.dilate(im, kernel, iterations = 1)
    # im = cv2.dilate(im, 2)
    
    # libimg.show(im)
    cv2.imwrite(outpath, im)
    
    # libimg.show(im)
    # stretch
    # im = cv2.normalize(im, None, 0, 1.0, cv2.NORM_MINMAX)

    # print im.min(), im.max()  # 0.0, 0.5294
    # # stretch the histogram - works
    # im2 = libimg.mpim2cv2(im)
    # equ = cv2.equalizeHist(im2)
    # im = libimg.cv22mpim(equ)
    # res = np.hstack((im2,equ)) #stacking images side-by-side
    # # cv2.imwrite('res.png',res)
    # libimg.show(res)
    # end

    # # show binarized image with bounding box
    # config.debugImages = True
    # th = 0.13
    # boundingBox = libimg.findBoundingBoxByBlob(im, th)

    # show image with best bounding box
    # config.debugImages = False
    # boundingBox = libimg.findBoundingBoxByBlob2(im, thdiff)
    
    # im2 = libimg.mpim2cv2(im)
    # im2 = libimg.gray2rgb(im2)
    # libimg.drawBoundingBox(im2, boundingBox)
    # libimg.show(im2)
    # cv2.imwrite(outpath, im2)






