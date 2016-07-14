
# unzip a specified Voyager archive volume


import os.path

import config
import lib

import vgBuildDownload


def buildUnzip(volnum):
    "Unzip the given volume number, if it doesn't exist yet."
    
    zipfilepath = config.downloadFolder + 'VGISS_' + str(volnum) + '.tar.gz' # eg  data/step1_downloads/vgiss_5101.tar.gz
    unzippedfolder = config.unzipFolder + 'VGISS_' + str(volnum) + '/'
    
    if os.path.isdir(unzippedfolder):
        print "Folder exists - skipping unzip step: " + unzippedfolder
    else:
        # download the zip if not already there
        vgBuildDownload.buildDownload(volnum)
        print "Unzipping " + zipfilepath
        print "       to " + unzippedfolder
        if int(volnum)==0:
            print "       (nothing to do - test volume 0)"
        else:
            lib.unzipFile(zipfilepath, unzippedfolder)


if __name__ == '__main__':
    os.chdir('..')
    buildUnzip(0)
    print 'done'
