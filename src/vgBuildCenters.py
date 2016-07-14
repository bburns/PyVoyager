
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
    imagespath = lib.getImagespath(volumeNum)
    centerspath = lib.getCenterspath(volumeNum)
    if int(volumeNum)==0: # test volume - turn on image debugging
        # config.drawBlob = True #. not working yet?
        # config.drawBoundingBox = True
        # config.drawCircle = True
        config.drawCrosshairs = True
    if int(volumeNum)!=0 and os.path.isdir(centerspath): # for test (vol=0), can overwrite folder
        print "Folder exists: " + centerspath
        return False
    else:
        # first build the plain images for the volume, if not already there
        buildImages(volumeNum)
        lib.mkdir(centerspath)
        nfile = 1
        for root, dirs, files in os.walk(imagespath):
            nfiles = len(files)
            del dirs[:] # don't recurse
            for filename in files: # eg C1385455_RAW_CLEAR.png
                ext = filename[-4:]
                if ext=='.png' or ext=='.PNG':
                    infile = imagespath + '/' + filename
                    outfile = centerspath + '/' + config.centersprefix + filename
                    print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                    # blobThreshold = config.blobThreshold
                    # fileid = filename.split('_')[0] # eg C1385455
                    # blobThreshold = getBlobThreshold(fileid)
                    # libimg.centerImageFile(infile, outfile, blobThreshold, config.rotateImage)
                    # libimg.centerImageFile(infile, outfile, config.rotateImage, config.centerMethod, config.drawBoundingBox, config.drawCrosshairs)
                    
                    libimg.centerImageFile(infile, outfile)
                    
                    # split into two phases
                    # im = libimg.loadImage(infile)
                    # if config.rotateImage:
                    #     im = np.rot90(im, 2) # rotate by 180
                    # bbox = libimg.findBoundingBox(im, config.centerMethod)
                    # #. write bbox to file
                    # # use bbox to center a (possibly) different image
                    # im = libimg.loadImage(filetocenter)
                    # im = libimg.centerImage(im, bbox)
                    # libimg.saveImage(outfile, im)
                    
                    nfile += 1
        return True



    
