
# convert Voyager IMG files to PNG files using img2png

import os.path

import config
import lib

import vgBuildUnzip


def buildImages(volnum):
    "Convert IMG files to PNG files for the given volume, if png folder doesn't exist yet."
    
    unzippedfolder = config.unzipFolder + 'VGISS_' + str(volnum) + '/'
    imagesfolder = config.imagesFolder + 'VGISS_' + str(volnum) + '/'
    
    if int(volnum)!=0 and os.path.isdir(imagesfolder):
        print "Images folder exists: " + imagesfolder
    else:
        # unzip the download, if not already there
        vgBuildUnzip.buildUnzip(volnum)
        
        # now convert the images
        datadir = unzippedfolder + 'DATA/'
        print "Converting imgs to pngs for " + datadir
        if int(volnum)==0:
            print '    (nothing to do - test volume 0 - manually populated)'
        else:
            lib.mkdir(imagesfolder) # create dest folder
            # for each subdir in datadir, cd subdir, run img2png on all img files in it
            i = 1
            for root, dirs, files in os.walk(datadir):
                ndirs = len(dirs)
                for subdir in dirs:
                    subdirabsolute = os.path.join(root, subdir)
                    subdirabsolute = os.path.abspath(dirpath)
                    print 'dir %d/%d: %s' % (i,ndirs,dirpath)
                    # for filespec in config.imageFilespecs: # eg ['*CALIB.IMG']
                        # libimg.img2png(subdirabsolute, filespec, imagesfolder, config.img2pngOptions)
                    libimg.img2png(subdirabsolute, config.imageFilespec, imagesfolder, config.img2pngOptions)
                    i += 1

    
if __name__ == '__main__':
    os.chdir('..')
    buildImages(0)
    print 'done'
