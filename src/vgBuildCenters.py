
# build centered images from plain images (pngs)

import os
import os.path

import config
import lib
import libimg
import db
    
import vgBuildImages


def buildCenters(volnum):
    "build centered images for given volume, if they don't exist yet"
    
    imagesubfolder = config.imagesFolder + 'VGISS_' + str(volnum) + '/'
    centersubfolder = config.centersFolder + 'VGISS_' + str(volnum) + '/'
    
    if int(volnum)==0: # test volume - turn on image debugging
        config.drawBlob = True
        config.drawCircle = True
        # config.drawBoundingBox = True
        config.drawCrosshairs = True
        
    if int(volnum)!=0 and os.path.isdir(centersubfolder): # for test (vol=0), can overwrite test folder
        print "Folder exists: " + centersubfolder
    else:
        # first build the plain images for the volume, if not already there
        vgBuildImages.buildImages(volnum)
        
        # now center the files
        #. this will work better if we're walking over the files.csv, approaches.csv, and thresholds.csv
        # at the same time, so can pass in more parameters
        # either that, or read them into a dictionary for the given volume first,
        # then grab the values when get to a file - less complex code that way
        lib.mkdir(centersubfolder)
        nfile = 1
        for root, dirs, files in os.walk(imagesubfolder):
            nfiles = len(files)
            del dirs[:] # don't recurse
            for pngfilename in files: # eg C1385455_RAW_CLEAR.png
                ext = pngfilename[-4:]
                if ext=='.png':
                    infile = imagesubfolder + pngfilename
                    outfile = centersubfolder + config.centersPrefix + pngfilename
                    print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                    libimg.centerImageFile(infile, outfile, config.centerMethod)
                    nfile += 1


if __name__ == '__main__':
    os.chdir('..')
    buildCenters(0)
    print 'done'


    
