
"""
vg unzip command

Unzip the specified Voyager archive volume.
"""

import os.path

import config
import lib

import vgDownload


def vgUnzip(filterVolume, overwrite=False, directCall=True):

    "Unzip the given volume number, if it doesn't exist yet."

    filterVolume = str(filterVolume)

    # get zipfilepath
    # eg data/step01_downloads/vgiss_5101.tar.gz
    # zipfilepath = config.downloadsFolder + 'VGISS_' + filterVolume + '.tar.gz'
    zipfilepath = config.folders['download'] + 'VGISS_' + filterVolume + '.tar.gz'
    # unzippedfolder = config.unzipsFolder + 'VGISS_' + filterVolume + '/'
    # inputSubfolder = lib.getSubfolder('download', filterVolume)
    outputSubfolder = lib.getSubfolder('unzip', filterVolume)

    # quit if volume folder exists
    # if os.path.isdir(unzippedfolder) and overwrite==False:
    if os.path.isdir(outputSubfolder) and overwrite==False:
        if directCall:
            print "Folder exists - skipping unzip step: " + outputSubfolder
        return

    # download the zip if not already there
    vgDownload.vgDownload(filterVolume, False, False) # not a direct call by the user

    # unzip the file
    print "Unzipping " + zipfilepath
    print "       to " + outputSubfolder
    # lib.rmdir(unzippedfolder)
    # lib.unzipFile(zipfilepath, unzippedfolder)
    lib.rmdir(outputSubfolder)
    lib.unzipFile(zipfilepath, outputSubfolder)


if __name__ == '__main__':
    os.chdir('..')
    vgUnzip(5101)
    print 'done'
