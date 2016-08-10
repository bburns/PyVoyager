
"""
vg unzip command

Unzip the specified Voyager archive volume.
"""

import os.path

import config
import lib

import vgDownload


def vgUnzip(volnum, overwrite=False, directCall=True):

    "Unzip the given volume number, if it doesn't exist yet."

    volnum = str(volnum)

    # get zipfilepath
    # eg data/step01_downloads/vgiss_5101.tar.gz
    zipfilepath = config.downloadsFolder + 'VGISS_' + volnum + '.tar.gz'
    unzippedfolder = config.unzipsFolder + 'VGISS_' + volnum + '/'

    # quit if volume folder exists
    if os.path.isdir(unzippedfolder) and overwrite==False:
        if directCall:
            print "Folder exists - skipping unzip step: " + unzippedfolder
        return

    # download the zip if not already there
    vgDownload.vgDownload(volnum, False, False) # not a direct call by the user

    # unzip the file
    print "Unzipping " + zipfilepath
    print "       to " + unzippedfolder
    lib.rmdir(unzippedfolder)
    lib.unzipFile(zipfilepath, unzippedfolder)


if __name__ == '__main__':
    os.chdir('..')
    vgUnzip(5101)
    print 'done'
