
# test centering routine
# usage: python testCentering.py



import cv2
import matplotlib.image as mpim # for imread, imsave
import scipy.misc as misc # for imsave - uses PIL - see http://stackoverflow.com/a/1713101/243392

import sys; sys.path.append('../src') # so can import from main src folder
import config
import lib
import libimg


# config.drawBlob = True
# config.drawCircle = True
# config.drawCircles = True
config.drawCrosshairs = True


testfolder = 'images/'
centeredfolder = testfolder + 'centered/'
thresholdedfolder = testfolder + 'thresholded/'
edgesfolder = testfolder + 'edges/'
maxerror = 2

# read in small csv file
results = lib.readCsv(testfolder + '_testfiles.csv')

ntestsok = 0
ntests = len(results)
fileids = results.keys() # not in any order
fileids.sort()
for fileid in fileids:
    
    infile = testfolder + fileid + '.png'
    centeredfile = centeredfolder + fileid + '.png'
    thresholdedfile = thresholdedfolder + fileid + '.png'
    edgesfile = edgesfolder + fileid + '.png'
    
    # any experimenting should be done in this routine
    boundingBox = libimg.centerImageFile(infile, centeredfile)
    x1,y1,x2,y2 = boundingBox

    # get binarization images (used by blob detector)
    im = mpim.imread(infile)
    b = 1*(im>config.blobThreshold)
    misc.imsave(thresholdedfile, b)
    
    # get canny edge images (used by hough detector)
    im = mpim.imread(infile)
    im2 = libimg.mpim2cv2(im)
    upper = config.cannyUpperThreshold
    lower = upper/2
    edges = cv2.Canny(im2, lower, upper)
    misc.imsave(edgesfile, edges)
    
    
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
        if deltax1<maxerror and deltay1<maxerror and deltax2<maxerror and deltay2<maxerror:
            print "[OK]     %s" % (fileid)
            ntestsok += 1
        else:
            print "[FAILED] %s, (%d, %d, %d, %d) expected (%d, %d, %d, %d)" % (fileid, x1,y1,x2,y2, x1best,y1best,x2best,y2best)
    else:
        print "[FAILED] " + fileid + ' ' + str(boundingBox)
        
print
print "Accuracy %0.1f%% (%d/%d tests passed)." % (ntestsok/float(ntests)*100, ntestsok, ntests)
print

