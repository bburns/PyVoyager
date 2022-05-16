"""
vg test composite command

Test of compositing routines.
"""

import cv2
import os
import math
import numpy as np

import config
import lib
import libimg


# from itertools import tee
# def pairs(iterable):
#     "s -> (s0,s1), (s1,s2), (s2, s3), ..."
#     # see https://docs.python.org/3/library/itertools.html#recipes
#     a, b = tee(iterable)
#     next(b, None)
#     next(b, None)
#     return zip(a, b)


def vgTestComposite():

    print 'Running compositing tests...'
    
    testCompositeDb = config.testFolder + 'testCompositeImages.csv'
    folder = config.testFolder + 'composite/'
    
    # open positions file
    # csvPositions, fPositions = lib.openCsvReader(config.dbPositions)
    
    # read in small csv file
    # csvTests = lib.readCsv(testCompositeDb) # test/testCenters.csv
    # ntests = len(csvTests)
    # ntestsok = 0
    maxerr = 8
    errsum = 0
    ntests = 0
    ntestsok = 0
    
    csvTests, fTests = lib.openCsvReader(testCompositeDb)
    for row in csvTests:
        # print row
        ntests += 1
        
        volume = row[0] # not used but helpful for csv file
        f0 = row[1]
        f1 = row[2]
        bestdx = int(row[3])
        bestdy = int(row[4])
        notes = row[5] if len(row)>5 else ''
        
        fileId = f0[:8]
        # print 'Testing',fileId
        
        f0 = folder + f0 + '.jpg'
        f1 = folder + f1 + '.jpg'
        im0 = cv2.imread(f0,0)
        im1 = cv2.imread(f1,0)
        assert not im0 is None
        assert not im1 is None

        # align im1 to im0
        dx,dy,ok = libimg.getImageAlignment(im0, im1)

        # show composite
        if ok:
            im1 = libimg.shiftImage(im1, dx, dy)
            blank = np.zeros((config.imsize,config.imsize),np.uint8)
            im = cv2.merge((im0,blank,im1))
            libimg.show(im,fileId)
        else:
            dx=dy=config.imsize/2 # just so avg px error isn't artificially low

        dx=-dx;dy=-dy

        # calculate error
        deltax = abs(dx-bestdx)
        deltay = abs(dy-bestdy)
        err = math.sqrt(deltax**2 + deltay**2)
        errsum += err
        if ok and err<maxerr:
            print "[OK]     %s: error %dpx [%s]" % (fileId,err,notes)
            ntestsok += 1
        else:
            print "[FAILED] %s: error %dpx - dx,dy (%d, %d) expected (%d, %d) [%s]" % \
                  (fileId, err, dx, dy, bestdx, bestdy, notes)
                
    fTests.close()
    
    accuracy = ntestsok/float(ntests)*100
    avgerror = errsum/float(ntests)
    print
    print "Accuracy %0.1f%% (%d/%d tests passed) - average error %dpx." % \
          (accuracy, ntestsok, ntests, avgerror)
    print


if __name__ == '__main__':
    os.chdir('..')
    vgTestComposite()
    print 'done'

