
# unzip a specified Voyager archive volume


import os.path

import config
import lib

import vgBuildDownload


def buildUnzip(volnum, overwrite=False):
    "Unzip the given volume number, if it doesn't exist yet."
    
    zipfilepath = config.downloadsFolder + 'VGISS_' + str(volnum) + '.tar.gz' # eg  data/step1_downloads/vgiss_5101.tar.gz
    unzippedfolder = config.unzipsFolder + 'VGISS_' + str(volnum) + '/'
    
    if os.path.isdir(unzippedfolder) and overwrite==False:
        print "Folder exists - skipping unzip step: " + unzippedfolder
    else:
        vgBuildDownload.buildDownload(volnum) # download the zip if not already there
        print "Unzipping " + zipfilepath
        print "       to " + unzippedfolder
        if int(volnum)==0:
            print "       (nothing to do - test volume 0)"
        else:
            lib.rmdir(unzippedfolder)
            lib.unzipFile(zipfilepath, unzippedfolder)


if __name__ == '__main__':
    os.chdir('..')
    buildUnzip(0)
    print 'done'
