
"""
vg unzip command

unzip a specified Voyager archive volume
"""

import os.path

import config
import lib

import vgDownload


def vgUnzip(volnum, overwrite=False, directCall=True):
    "Unzip the given volume number, if it doesn't exist yet."

    # get zipfile eg data/step1_downloads/vgiss_5101.tar.gz
    zipfilepath = config.downloadsFolder + 'VGISS_' + str(volnum) + '.tar.gz'
    unzippedfolder = config.unzipsFolder + 'VGISS_' + str(volnum) + '/'

    if os.path.isdir(unzippedfolder) and overwrite==False:
        if directCall:
            print "Folder exists - skipping unzip step: " + unzippedfolder
    else:
        # download the zip if not already there
        vgDownload.vgDownload(volnum, False, False)

        print "Unzipping " + zipfilepath
        print "       to " + unzippedfolder
        if int(volnum)==0:
            print "       (nothing to do - test volume 0)"
        else:
            lib.rmdir(unzippedfolder)
            lib.unzipFile(zipfilepath, unzippedfolder)


if __name__ == '__main__':
    os.chdir('..')
    vgUnzip(0)
    print 'done'
