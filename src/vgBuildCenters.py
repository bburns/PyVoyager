
# build centered images from plain images (pngs)


import os
import os.path

import config
import lib
import libimg
import db
    
from vgBuildImages import buildImages



def buildCenters(volumeNum):
    "build centered images for given volume, if they don't exist yet"
    volumeNum = int(volumeNum)
    volumeStr = str(volumeNum)
    imageType = 'Calib'
    imagespath = config.imagesFolder + '/VGISS_' + volumeStr
    centerspath = config.centersFolder + '/VGISS_' + volumeStr
    if volumeNum==0: # test volume - turn on image debugging
        # config.drawBlob = True #. not working yet?
        # config.drawBoundingBox = True
        # config.drawCircle = True
        config.drawCrosshairs = True
    if volumeNum!=0 and os.path.isdir(centerspath): # for test (vol=0), can overwrite test folder
        print "Folder exists: " + centerspath
        return False
    else:
        # first build the plain images for the volume, if not already there
        buildImages(volumeNum)
        # now center the files
        lib.mkdir(centerspath)
        nfile = 1
        for root, dirs, files in os.walk(imagespath):
            nfiles = len(files)
            del dirs[:] # don't recurse
            for filename in files: # eg C1385455_RAW_CLEAR.png
                ext = filename[-4:].lower()
                if ext=='.png':
                    infile = imagespath + '/' + filename
                    outfile = centerspath + '/' + config.centersprefix + filename
                    print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                    
                    # blobThreshold = config.blobThreshold
                    # fileid = filename.split('_')[0] # eg C1385455
                    # blobThreshold = getBlobThreshold(fileid)
                    # libimg.centerImageFile(infile, outfile, blobThreshold, config.rotateImage)
                    # libimg.centerImageFile(infile, outfile, config.rotateImage, config.centerMethod, config.drawBoundingBox, config.drawCrosshairs)
                    
                    # libimg.centerImageFile(infile, outfile)
                    boundingBox = libimg.centerImageFile(infile, outfile)
                    print infile, boundingBox
                    
                    nfile += 1
        return True


if __name__ == '__main__':
    os.chdir('..')
    buildCenters(5101)
    print 'done'


    
