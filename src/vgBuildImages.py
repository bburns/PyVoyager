
# convert Voyager IMG files to PNG files using img2png


import os.path

import config
import lib

from vgBuildUnzip import buildUnzip


def buildImages(volumeNum):
    "convert IMG files to PNG files, if folder doesn't exist yet"
    volumeNum = int(volumeNum)
    volumeStr = str(volumeNum)
    imageType = 'Calib' #. default
    # unzippedpath = lib.getUnzippedpath(volumeNum)
    # imagespath = lib.getImagespath(volumeNum)
    unzippedpath = config.unzipFolder + '/VGISS_' + volumeStr
    imagespath = config.imagesFolder + '/' + imageType + '/VGISS_' + volumeStr
    if int(volumeNum)==0: # do nothing if asking for test volume
        print 'Volume 0 is a test volume, which should be manually created in step3_images/test,'
        print 'and populated with test cases for centering, etc.'
        print
    elif os.path.isdir(imagespath):
        print "Images folder exists: " + imagespath
        return False
    else:
        # unzip the download, if not already there
        buildUnzip(volumeNum)
        # now convert the images
        lib.mkdir(imagespath) # create folder
        datadir = unzippedpath + '/DATA'
        print "Converting imgs to pngs for " + datadir
        # for each subdir in datadir, cd subdir, run img2png on all img files in it
        i = 1
        # filespec = config.imageFilespec # eg "*RAW.IMG"
        for root, dirs, files in os.walk(datadir):
            ndirs = len(dirs)
            for subdir in dirs:
                dirpath = os.path.join(root, subdir)
                dirpath = os.path.abspath(dirpath)
                print 'dir %d/%d: %s' % (i,ndirs,dirpath)
                for filespec in config.imageFilespecs:
                    lib.img2png(dirpath, filespec, imagespath, config.img2pngOptions)
                i += 1
        return True

    
if __name__ == '__main__':
    os.chdir('..')
    buildImages(5101)
    print 'done'
