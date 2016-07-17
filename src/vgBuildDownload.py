
# download tar.gz archives from pds rings site at seti.org

import os
import os.path

import config
import lib


def buildDownload(volnum, overwrite=False):
    "Download the given volume number, if it doesn't exist yet."
    
    url = lib.getDownloadUrl(volnum) # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    filepath = config.downloadsFolder + filetitle # eg data/step1_downloads/VGISS_5101.tar.gz
    
    if os.path.isfile(filepath) and overwrite==False:
        print "File exists - skipping download step: " + filepath
    else:
        print "Downloading " + url
        print "         to " + filepath
        if int(volnum)==0:
            print "         (nothing to do - test volume 0)"
        else:
            lib.rm(filepath)
            lib.downloadFile(url, filepath)


if __name__ == '__main__':
    os.chdir('..')
    buildDownload(0)
    print 'done'
