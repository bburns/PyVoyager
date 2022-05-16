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

    # get zipfilepath, eg 'data/step01_downloads/VGISS_5101.tar.gz'
    zipfilepath = config.folders['download'] + 'VGISS_' + volnum + '.tar.gz'

    # get output location, eg 'data/step02_unzip/VGISS_5101/'
    outputSubfolder = lib.getSubfolder('unzip', volnum)

    # quit if volume folder exists
    if os.path.isdir(outputSubfolder) and overwrite==False:
        if directCall: print "Folder exists: " + outputSubfolder
        return

    # download the zipfile if not already there
    vgDownload.vgDownload(volnum, overwrite=False, directCall=False)

    # unzip the file
    print "Unzipping " + zipfilepath
    print "       to " + outputSubfolder
    lib.rmdir(outputSubfolder)
    lib.unzipFile(zipfilepath, outputSubfolder)


if __name__ == '__main__':
    os.chdir('..')
    vgUnzip(5101)
    print 'done'
