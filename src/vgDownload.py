
"""
vg download command

Download tar.gz archives from PDS ring site at seti.org
"""

import os
import os.path

import config
import lib


# def vgDownload(volnum, imageId, targetPath, overwrite=False, directCall=True):
# def vgDownload(volnum, options, directCall=True):
def vgDownload(volnum, overwrite=False, directCall=True):

    "Download the given volume number, if it doesn't exist yet."

    volnum = str(volnum)
    # overwrite = options.get('overwrite')

    # get url
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    url = lib.getDownloadUrl(volnum)
    filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    filepath = config.downloadsFolder + filetitle # eg data/step1_downloads/VGISS_5101.tar.gz

    # quit if volume folder exists
    if os.path.isfile(filepath) and overwrite==False:
        if directCall:
            print "File exists - skipping download step: " + filepath
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
