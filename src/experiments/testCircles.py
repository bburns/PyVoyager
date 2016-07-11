
# tests of hough circle detection

import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg


folder = 'images/'
maxerror = 2

# read in csv file to dict of dicts
results = lib.readCsv('images/results.csv')
# print results

ntestsok = 0
ntests = len(results)
for fileid in results:
    
    # get expected results
    result = results[fileid]
    xbest = int(result['x'])
    ybest = int(result['y'])
    rbest = int(result['radius'])
    
    # load image
    filepath = folder + fileid + '.png'
    im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE) # values are 0-255

    # blur image to diminish reseau marks
    kernelSize = 5 # aperture size - should be odd
    gaussianSigma = 7
    im = cv2.GaussianBlur(im, (kernelSize, kernelSize), gaussianSigma)

    #. maybe do a pre-canny step here? 
    # lower = 100
    # upper = 200
    # im = cv2.Canny(im, lower, upper)

    # libimg.show(im)
    
    # find 'best' circle
    circle = libimg.findCircle(im) # (x,y,r)
    if type(circle) == type(None):
        circle=(0,0,0)
    x,y,r = circle
        
    # calculate error
    deltax = abs(x-xbest)
    deltay = abs(y-ybest)
    deltar = abs(r-rbest)
    
    # show message
    if deltax<maxerror and deltay<maxerror and deltar<maxerror:
        print "[OK]     %s, (%d, %d, %d)" % (fileid, x, y, r)
        ntestsok += 1
    else:
        print "[FAILED] %s, (%d, %d, %d) should be (%d, %d, %d)" % (fileid, x,y,r, xbest, ybest, rbest)
        
print
print "%d/%d tests passed." % (ntestsok, ntests)
print

