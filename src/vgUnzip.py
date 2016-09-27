
"""
vg unzip command

Unzip the specified Voyager archive volume.
"""

import os.path

import config
import lib

import vgDownload


def vgUnzip(edrVol, overwrite=False, directCall=True):

    "Unzip the given EDR volume number, if it doesn't exist yet."

    # get zipfilepath, eg data/step01_downloads/vg_0013.tar.gz
    edrVol = int(edrVol)
    zipfilepath = lib.getFolder('download') + 'VG_%04d.tar.gz' % edrVol

    # get output location
    outputSubfolder = lib.getSubfolder('unzip', edrVol)

    # quit if volume folder exists
    if os.path.isdir(outputSubfolder) and overwrite==False:
        if directCall: print "Folder exists: " + outputSubfolder
        return

    # download the zipfile if not already there
    vgDownload.vgDownload(edrVol, overwrite=False, directCall=False)

    # unzip the file
    print "Unzipping " + zipfilepath
    print "       to " + outputSubfolder
    lib.rmdir(outputSubfolder)
    lib.unzipFile(zipfilepath, outputSubfolder)


if __name__ == '__main__':
    os.chdir('..')
    vgUnzip(5101)
    print 'done'
