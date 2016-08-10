
"""
vg test center command

Test of centering routines.
Any experimenting with settings should be done in centerImageFile or config settings.
"""

import cv2
import os

import config
import lib
import libimg


def vgTestCenter():

    print 'Running centering tests...'
    
    maxerror = 2

    # config.drawBinaryImage = True
    # config.drawBoundingBox = True
    # config.drawEdges = True
    # config.drawCircles = True
    # config.drawCircle = True
    config.drawCrosshairs = True

    centeredFolder = config.testCenterImagesFolder + 'centered/'
    debugFolder = config.testCenterImagesFolder + 'debug/'

    #. fix this weird issue with access denied
    lib.rmdir(centeredFolder)
    lib.mkdir(centeredFolder)
    # os.mkdir(centeredFolder)

    lib.rmdir(debugFolder)
    lib.mkdir(debugFolder) # if folder is open in explorer will end up with no debugfolder!
    # os.mkdir(debugFolder)

    # open positions file
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)
    
    # read in small csv file
    results = lib.readCsv(config.testCenterdb) # test/testCenters.csv
    ntests = len(results)
    ntestsok = 0

    for root, dirs, files in os.walk(config.testCenterImagesFolder): # test/center
        for filename in files:

            ext = filename[-4:].lower()
            if ext=='.jpg' or ext=='.png':

                fileId = filename[:8] # eg C1328423
                fileTitle = filename[:-4] # eg C1328423_neptune_dim
                infile = config.testCenterImagesFolder + filename
                centeredFile = centeredFolder + filename
                debugTitle = debugFolder + fileTitle
                config.debugImageTitle = debugTitle

                rowPositions = lib.getJoinRow(csvPositions, config.positionsColFileId, fileId)
                if rowPositions:
                    # fraction of frame
                    imageFraction = float(rowPositions[config.positionsColImageFraction]) 
                    radius = int(400*imageFraction) #.param
                else:
                    radius = None
                
                x,y,r = libimg.centerImageFile(infile, centeredFile, radius)

                if rowPositions:
                    # draw a yellow circle on centeredFile to mark expected target size
                    im = cv2.imread(centeredFile)
                    circle = (399,399,radius) #.params
                    libimg.drawCircle(im, circle, color = (0,255,255))
                    cv2.imwrite(centeredFile, im)
                
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
                            # print "[OK]     %s" % (fileTitle)
                            ntestsok += 1
                        else:
                            print "[FAILED] %s, (%d, %d) expected (%d, %d)" % \
                                  (fileTitle, x, y, xbest, ybest)
                    else:
                        print     "[NO XY]  %s,%d,%d" % (fileTitle, x, y)
                else:
                    print         "[NO REC] %s,%d,%d" % (fileTitle, x, y)

        del dirs[:] # don't recurse

    fPositions.close()
    print
    accuracy = ntestsok/float(ntests)*100
    print "Accuracy %0.1f%% (%d/%d tests passed)." % (accuracy, ntestsok, ntests)
    print


if __name__ == '__main__':
    os.chdir('..')
    vgTestCenter()
    print 'done'

