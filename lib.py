
# library routines for pyvoyager
# used by different files

import os # for system
import os.path # for isfile
from setuptools import archive_util # for unpack_archive


import config # constants


def download_file(url, filepath):
    "download a file from a url to a given filepath"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    if os.path.isfile(filepath):
        print "file " + filepath + " already exists"
        return False
    else:
        cmd = "curl -o " + filepath + " " + url
        os.system(cmd)
        return True


def get_download_url(volnumber):
    "get url to download a volume"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    volprefix = str(volnumber)[0:1] # first digit (=planet number)
    url = config.download_url.format(volprefix, volnumber)
    return url


def get_volume_title(volnumber):
    return "VGISS_" + str(volnumber)


def get_zipfilepath(volnumber):
    "get filepath for zipfile corresponding to a volume number"
    # eg c:/users/bburns/desktop/voyager/step0_downloads/VGISS_5101.tar.gz
    sourcefolder = config.download_folder
    url = get_download_url(volnumber)
    filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    zipfilepath = sourcefolder + "/" + filetitle
    return zipfilepath
    

def get_unzippedpath(volnumber):
    "get folder path for unzipped volume"
    # eg c:/users/bburns/desktop/voyager/step1_unzips/VGISS_5101
    unzipfolder = config.unzip_folder
    url = get_download_url(volnumber)
    filetitle = get_volume_title(volnumber)
    unzippedpath = unzipfolder + '/' + filetitle
    return unzippedpath


def get_pngpath(volnumber):
    "get folder path for png images"
    # eg c:/users/bburns/desktop/voyager/step2_pngs/VGISS_5101
    pngfolder = config.png_folder
    filetitle = get_volume_title(volnumber)
    pngpath = pngfolder + '/' + filetitle
    return pngpath


def unzip_file(zipfile, destfolder):
    """unzip a file to a destination folder.
    assumes zip file is a .tar or .tar.gz file.
    doesn't unzip file if destination folder already exists.
    eg unzip_file('test/unzip_test.tar', 'test/unzip_test')"""
    #. but note - tar file can have a top-level folder, or not -
    # this is assuming that it does, which is why we extract the tarfile
    # to the parent folder of destfolder.
    if os.path.isdir(destfolder):
        print "Folder " + destfolder + " already exists - not unzipping"
        return False
    else:
        #. tried just building a commandline cmd but had issues with windows paths etc
        # os.mkdir(destfolder)
        # archive_util.unpack_archive(zipfile, destfolder)
        parentfolder = destfolder + "/.."
        archive_util.unpack_archive(zipfile, parentfolder)
        return True

    
def test():
    print get_download_url(5101)
    print get_zipfilepath(5101)
    print get_unzippedpath(5101)
    print get_pngpath(5101)
    
    #. test this with a tar.gz
    print 'unzipping test file...'
    unzip_file('test/unzip_test.tar', 'test/unzip_test')
    print 'All done.'
    
if __name__ == '__main__':
    test()



