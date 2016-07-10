
# unzip a specified Voyager archive volume


import os.path

import lib

from vgBuildDownload import buildDownload


def buildUnzip(volumeNum):
    "unzip the given volume number, if it doesn't exist yet"
    if int(volumeNum)==0:
        print 'test volume is to be created manually'
        print
    else:
        zipfilepath = lib.getZipfilepath(volumeNum)
        unzippedpath = lib.getUnzippedpath(volumeNum)
        if os.path.isdir(unzippedpath):
            print "Folder exists: " + unzippedpath
            return False
        else:
            # download the zip if not already there
            buildDownload(volumeNum)
            print "Unzipping " + zipfilepath
            print "       to " + unzippedpath
            return lib.unzipFile(zipfilepath, unzippedpath)

