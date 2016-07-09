
import os.path

import config
import lib


def buildDownload(volumeNum):
    "download the given volume number, if it doesn't exist yet"
    # eg buildZip(5101)
    if int(volumeNum)==0:
        print 'test volume is to be constructed manually'
        print
    else:
        destfolder = config.downloadFolder
        url = lib.getDownloadUrl(volumeNum) # eg http://.....
        zipfilepath = lib.getZipfilepath(volumeNum) # eg  ../data/step1_downloads/vgiss_5101
        filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
        filepath = destfolder + "/" + filetitle
        if os.path.isfile(filepath):
            print "File exists: " + filepath
            return False
        else:
            print "Downloading " + url
            print "         to " + filepath
            return lib.downloadFile(url, filepath)

