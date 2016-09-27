
"""
vg download command

Download tar.gz archives from PDS ring site at seti.org
"""

import os
import os.path

import config
import lib


def vgDownload(edrVol, overwrite=False, directCall=True):

    "Download the given EDR volume number, if it doesn't exist yet."

    edrVol = str(edrVol)

    # get url
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    url = lib.getDownloadUrl(edrVol)

    # get download location
    filetitle = url.split('/')[-1] # eg VG_0013.tar.gz
    filepath = lib.getFolder('download') + filetitle # eg data/step01_download/VG_0013.tar.gz

    # quit if volume folder exists
    if os.path.isfile(filepath) and overwrite==False:
        if directCall: print "File exists: " + filepath
        return

    # download the volume
    print "Downloading " + url
    print "         to " + filepath
    lib.rm(filepath)
    lib.downloadFile(url, filepath)


if __name__ == '__main__':
    os.chdir('..')
    vgDownload(5101)
    print 'done'
