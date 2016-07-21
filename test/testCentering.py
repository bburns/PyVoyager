
# test of centering routines
# usage: python testCentering.py
# or run with 'vg test'


import cv2
import matplotlib.image as mpim # for imread, imsave
import scipy.misc as misc # for imsave - uses PIL - see http://stackoverflow.com/a/1713101/243392

import sys; sys.path.append('../src') # so can import from main src folder
import config
import lib
import libimg


def testCentering():

    config.drawBinaryImage = True
    config.drawBoundingBox = True
    config.drawEdges = True
    config.drawCircles = True
    config.drawCircle = True
    config.drawCrosshairs = True

    testfolder = 'images/'
    centeredfolder = testfolder + 'centered/'
    debugfolder = testfolder + 'debug/'
    maxerror = 2

    # read in small csv file
    results = lib.readCsv('testfiles.csv')

    ntestsok = 0
    ntests = len(results)
    fileids = results.keys() # not in any order
    fileids.sort()
    for fileid in fileids:

        infile = testfolder + fileid + '.png'
        centeredfile = centeredfolder + fileid + '.png'

        # any experimenting should be done in centerImageFile or config settings
        debugtitle = debugfolder + fileid
        boundingBox = libimg.centerImageFile(infile, centeredfile, debugtitle)
        x1,y1,x2,y2 = boundingBox

        # get expected results
        result = results[fileid]
        if result.get('x1'):
            x1best = int(result['x1'])
            x2best = int(result['x2'])
            y1best = int(result['y1'])
            y2best = int(result['y2'])

            # calculate error
            deltax1 = abs(x1-x1best)
            deltay1 = abs(y1-y1best)
            deltax2 = abs(x2-x2best)
            deltay2 = abs(y2-y2best)

            # show message
            if deltax1<=maxerror and deltay1<=maxerror and deltax2<=maxerror and deltay2<=maxerror:
                print "[OK]     %s" % (fileid)
                ntestsok += 1
            else:
                print "[FAILED] %s, (%d, %d, %d, %d) expected (%d, %d, %d, %d)" % \
                      (fileid, x1,y1,x2,y2, x1best,y1best,x2best,y2best)
        else:
            print "[FAILED] " + fileid + ' ' + str(boundingBox)

    print
    print "Accuracy %0.1f%% (%d/%d tests passed)." % (ntestsok/float(ntests)*100, ntestsok, ntests)
    print


if __name__ == '__main__':
    # os.chdir('..')
    testCentering()
    print 'done'

