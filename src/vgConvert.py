
# vg convert command
# convert Voyager IMG files to PNG files using img2png

import os.path

import config
import lib
import libimg

import vgUnzip


def vgConvert(volnum, overwrite=False, directCall=True):
    "Convert IMG files to PNG files for the given volume, if png folder doesn't exist yet."

    unzippedSubfolder = config.unzipsFolder + 'VGISS_' + str(volnum) + '/'
    imagesSubfolder = config.imagesFolder + 'VGISS_' + str(volnum) + '/'

    if int(volnum)!=0 and os.path.isdir(imagesSubfolder) and overwrite==False:
        if directCall:
            print "Images folder exists: " + imagesSubfolder
    else:
        # unzip the download, if not already there
        vgUnzip.vgUnzip(volnum, False, False)

        # now convert the images
        lib.rmdir(imagesSubfolder)
        datadir = unzippedSubfolder + 'DATA/'
        print "Converting imgs to pngs for " + datadir
        if int(volnum)==0:
            print '    (nothing to do - test volume 0 - manually populated)'
        else:
            lib.mkdir(imagesSubfolder) # create dest folder
            # for each subdir in datadir, cd subdir, run img2png on all img files in it
            i = 1
            for root, dirs, files in os.walk(datadir):
                ndirs = len(dirs)
                for subdir in dirs:
                    subdir = os.path.join(root, subdir)
                    subdirabsolute = os.path.abspath(subdir)
                    print 'Directory %d/%d: %s          \r' % (i,ndirs,subdirabsolute),
                    # for filespec in config.imageFilespecs: # eg ['*CALIB.IMG']
                        # libimg.img2png(subdirabsolute, filespec, imagesSubfolder,
                                       # config.img2pngOptions)
                    libimg.img2png(subdirabsolute, config.imageFilespec,
                                   imagesSubfolder, config.img2pngOptions)
                    i += 1
            print


if __name__ == '__main__':
    os.chdir('..')
    vgConvert(0)
    print 'done'

