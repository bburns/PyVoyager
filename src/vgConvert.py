
"""
vg convert command

Convert Voyager IMG files to PNG files using img2png.
"""

import os.path

import config
import lib
import libimg

import vgUnzip


# def vgConvert(volnum, imageId=None, targetPath=None, overwrite=False, directCall=True):
def vgConvert(volnum, overwrite=False, directCall=True):

    "Convert IMG files to PNG files for the given volume, if png folder doesn't exist yet."

    volnum = str(volnum)
    unzippedSubfolder = config.unzipsFolder + 'VGISS_' + volnum + '/'
    imagesSubfolder = config.imagesFolder + 'VGISS_' + volnum + '/'

    # quit if volume folder exists
    if os.path.isdir(imagesSubfolder) and overwrite==False:
        if directCall:
            print "Images folder exists: " + imagesSubfolder
        return

    # unzip the download, if not already there
    vgUnzip.vgUnzip(volnum, False, False) # not a direct call by the user

    # now convert the images

    # create dest folder
    lib.rmdir(imagesSubfolder)
    lib.mkdir(imagesSubfolder)

    datadir = unzippedSubfolder + 'DATA/'
    print "Converting imgs to pngs for " + datadir

    # for each subdir in datadir, cd subdir, run img2png on all img files in it
    ndir = 1
    for root, dirs, files in os.walk(datadir):
        ndirs = len(dirs)
        for subdir in dirs:
            subdir = os.path.join(root, subdir)
            subdirabsolute = os.path.abspath(subdir)
            print 'Directory %d/%d: %s          \r' % (ndir,ndirs,subdirabsolute),
            # libimg.img2png(subdirabsolute, config.imageFilespec,
                           # imagesSubfolder, config.img2pngOptions)
            for filespec in config.imageFilespecs: # eg ['*RAW.IMG','*CALIB.IMG']
                libimg.img2png(subdirabsolute, filespec, imagesSubfolder,
                               config.img2pngOptions)
            ndir += 1
    print


if __name__ == '__main__':
    os.chdir('..')
    vgConvert(5101)
    print 'done'

