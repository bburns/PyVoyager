
# library routines for pyvoyager
# used by different files

import os # for system, mkdir, mkdirs
import os.path # for isfile
from setuptools import archive_util # for unpack_archive
import errno
import re # for findall


#.. should pass any constants into functions - this is a cheat
import config # constants


img2pngOptions = "-fnamefilter" # append filter name, eg _ORANGE

def img2png(src, filespec, dst):
    "Convert all IMG files matching filespec in src dir to PNG files in the dest dir"
    # first convert img's to png's, then move them to the dest dir
    import os
    savedir = os.getcwd()
    os.chdir(src)
    # eg "img2png *.img -fnamefilter"
    cmd = "img2png " + filespec + " " + img2pngOptions
    print cmd
    os.system(cmd)
    # now move the png files to pngpath
    os.chdir(savedir)
    cmd = "move " + src +"\\*.png " + dst + "/"
    print cmd
    os.system(cmd)


def splitId(itemId):
    "Split an id like 'movie15' into ['movie','15']"
    itemType, itemNum = re.findall(r"[^\W\d_]+|\d+", itemId)
    return [itemType, itemNum]



def copyFilesSequenced(src, dst, filenamePattern):
    "Copy all files from src to dst folders, numbering sequentially using given pattern"
    # used for staging files for use by ffmpeg
    # eg pattern = 'img%04d.png'
    mkdir(dst)
    # copy files, numbering them sequentially
    # (wasteful, but necessary as ffmpeg doesn't handle globbing on windows)
    i = 1
    for root, dirs, files in os.walk(src):
        nfiles = len(files)
        for infile in files:
            inpath = src + '/' + infile
            # print inpath
            # outfile = 'img%04d.png' % i
            outfile = filenamePattern % i
            outpath = dst + '/' + outfile
            # print outpath
            # print 'copy ' + str(i) + ': ' + inpath
            cmd = "cp " + inpath + " " + outpath
            # print cmd
            os.system(cmd)
            # print 'copied ' + str(i) + ': ' + outpath
            print 'copied %d/%d: %s' % (i,nfiles,outpath)
            i += 1
    


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
        
def pngsToMp4(folder, filenamePattern, outputFilename, frameRate):
    "Convert a sequentially numbered set of pngs to an mp4 movie"
    os.chdir(folder)
    # eg "ffmpeg -y -i img%04d.png -r 15 a.mp4"
    cmd = 'ffmpeg -y -i %s -r %d %s' % (filenamePattern, frameRate, outputFilename)
    print cmd
    os.system(cmd)



def downloadFile(url, filepath):
    "download a file from a url to a given filepath using curl"
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
    if int(volnumber)==0:
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


def getImagespath(volnumber):
    "get folder path for png images"
    # eg c:/users/bburns/desktop/voyager/step2_pngs/VGISS_5101
    imagesfolder = config.imagesFolder
    filetitle = getVolumeTitle(volnumber)
    imagespath = imagesfolder + '/' + filetitle
    return imagespath


def getCenterspath(volnumber):
    "get folder path for centered images"
    # eg c:/users/bburns/desktop/voyager/step3_centered/VGISS_5101
    centersfolder = config.centersFolder
    filetitle = getVolumeTitle(volnumber)
    centerspath = centersfolder + '/' + filetitle
    return centerspath


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
    print getDownloadUrl(5101)
    print getZipfilepath(5101)
    print getUnzippedpath(5101)
    print getImagespath(5101)
    print getImagespath(0)
    print getCenterspath(5101)
    
    #. test this with a tar.gz
    # print 'unzipping test file...'
    # unzipFile('test/unzip_test.tar', 'test/unzip_test')
    # print 'All done.'
    
if __name__ == '__main__':
    test()



