
# library routines for pyvoyager
# used by different files

import os # for system, mkdir, mkdirs
import os.path # for isfile
from setuptools import archive_util # for unpack_archive
import errno

import config # constants



def mkdir(path):
    "Make a directory, ignoring any errors (eg if it already exists)"
    try:
        os.mkdir(path) 
    except:
        pass

def mkdir_p(path):
    "Make a directory tree, ignoring any errors (eg if it already exists)"
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
        
def pngsToMp4(folder, imageFilespec, frameRate, outputFilename):
    "convert a sequentially numbered set of pngs to an mp4 movie"
    os.chdir(folder)
    # eg "ffmpeg -y -i img%04d.png -r 15 a.mp4"
    cmd = 'ffmpeg -y -i %s -r %d %s' % (imageFilespec, frameRate, outputFilename)
    print cmd
    os.system(cmd)



def downloadFile(url, filepath):
    "download a file from a url to a given filepath"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    if os.path.isfile(filepath):
        print "file " + filepath + " already exists"
        return False
    else:
        cmd = "curl -o " + filepath + " " + url
        print cmd
        os.system(cmd)
        return True


def getDownloadUrl(volnumber):
    "get url to download a volume"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    volprefix = str(volnumber)[0:1] # first digit (=planet number)
    url = config.downloadUrl.format(volprefix, volnumber)
    return url


def getVolumeTitle(volnumber):
    if volnumber==0:
        return "test"
    else:
        return "VGISS_" + str(volnumber)


def getZipfilepath(volnumber):
    "get filepath for zipfile corresponding to a volume number"
    # eg c:/users/bburns/desktop/voyager/step0_downloads/VGISS_5101.tar.gz
    sourcefolder = config.downloadFolder
    url = getDownloadUrl(volnumber)
    filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    zipfilepath = sourcefolder + "/" + filetitle
    return zipfilepath
    

def getUnzippedpath(volnumber):
    "get folder path for unzipped volume"
    # eg c:/users/bburns/desktop/voyager/step1_unzips/VGISS_5101
    unzipfolder = config.unzipFolder
    url = getDownloadUrl(volnumber)
    filetitle = getVolumeTitle(volnumber)
    unzippedpath = unzipfolder + '/' + filetitle
    return unzippedpath


def getPngpath(volnumber):
    "get folder path for png images"
    # eg c:/users/bburns/desktop/voyager/step2_pngs/VGISS_5101
    pngfolder = config.pngFolder
    filetitle = getVolumeTitle(volnumber)
    pngpath = pngfolder + '/' + filetitle
    return pngpath

def getCenteredpath(volnumber):
    "get folder path for centered images"
    # eg c:/users/bburns/desktop/voyager/step3_centered/VGISS_5101
    centeredfolder = config.centeredFolder
    filetitle = getVolumeTitle(volnumber)
    centeredpath = centeredfolder + '/' + filetitle
    return centeredpath


def unzipFile(zipfile, destfolder):
    """unzip a file to a destination folder.
    assumes zip file is a .tar or .tar.gz file.
    doesn't unzip file if destination folder already exists.
    eg unzipFile('test/unzip_test.tar', 'test/unzip_test')"""
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
    print getDownload_url(5101)
    print getZipfilepath(5101)
    print getUnzippedpath(5101)
    print getPngpath(5101)
    print getPngpath(0)
    
    #. test this with a tar.gz
    print 'unzipping test file...'
    unzipFile('test/unzip_test.tar', 'test/unzip_test')
    print 'All done.'
    
if __name__ == '__main__':
    test()



