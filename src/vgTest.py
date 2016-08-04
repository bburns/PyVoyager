
"""
vg test command

Test of centering routines.
Any experimenting with settings should be done in centerImageFile or config settings.
"""

import cv2
import matplotlib.image as mpim # for imread, imsave
import scipy.misc as misc # for imsave - uses PIL - see http://stackoverflow.com/a/1713101/243392
import os

# import sys; sys.path.append('../src') # so can import from main src folder
import config
import lib
import libimg


def vgTest():

    print 'Running centering tests...'
    
    maxerror = 2

    config.drawBinaryImage = True
    config.drawBoundingBox = True
    config.drawEdges = True
    config.drawCircles = True
    config.drawCircle = True
    config.drawCrosshairs = True

    centeredFolder = config.testImagesFolder + 'centered/'
    debugFolder = config.testImagesFolder + 'debug/'

    lib.rmdir(centeredFolder)
    lib.mkdir(centeredFolder)

    lib.rmdir(debugFolder)
    os.mkdir(debugFolder)

    # read in small csv file
    # results = lib.readCsv('test/testImages.csv')
    results = lib.readCsv(config.testImagesdb) # test/testImages.csv
    ntests = len(results)
    ntestsok = 0

    # for root, dirs, files in os.walk(testFolder):
    for root, dirs, files in os.walk(config.testImagesFolder): # test/images
        for filename in files:

            ext = filename[-4:]
            if ext=='.jpg' or ext=='.png':

                fileId = filename[:8] # eg C1328423
                fileTitle = filename[:-4] # eg C1328423_neptune_dim
                # infile = testFolder + filename
                infile = config.testImagesFolder + filename
                centeredFile = centeredFolder + filename
                debugTitle = debugFolder + fileTitle

                x, y, radius = libimg.centerImageFile(infile, centeredFile, debugTitle)

                # get expected results
                result = results.get(fileTitle)
                if result != None:
                    if result.get('x'):
                        xbest = int(result['x'])
                        ybest = int(result['y'])

                        # calculate error
                        deltax = abs(x-xbest)
                        deltay = abs(y-ybest)

                        # show message
                        if deltax <= maxerror and deltay <= maxerror:
                            print "[OK]     %s" % (fileTitle)
                            ntestsok += 1
                        else:
                            print "[FAILED] %s, (%d, %d) expected (%d, %d)" % \
                                  (fileTitle, x, y, xbest, ybest)
                    else:
                        print     "[NO XY]  %s,%d,%d" % (fileTitle, x, y)
                else:
                    print         "[NO REC] %s,%d,%d" % (fileTitle, x, y)

        del dirs[:] # don't recurse

    print
    accuracy = ntestsok/float(ntests)*100
    print "Accuracy %0.1f%% (%d/%d tests passed)." % (accuracy, ntestsok, ntests)
    print


if __name__ == '__main__':
    os.chdir('..')
    vgTest()
    print 'done'

