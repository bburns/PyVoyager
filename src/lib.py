
# library routines for voyager


import os # for system, mkdir, mkdirs
import os.path # for isfile
from setuptools import archive_util # for unpack_archive
import errno
import re # for findall
import csv

#.. should pass any constants into functions!
import config


def readCsv(filename):
    "read a csv file into a dict of dicts. first column is key. use on small files only."
    # comments or blank lines are skipped
    f = open(filename, 'rt')
    i = 0
    items = {}
    reader = csv.reader(f)
    for row in reader:
        if row==[] or row[0][0]=='#': # skip blank lines and comments
            continue
        if i==0:
            fields = row
        else:
            j = 0
            item = {}
            for value in row:
                if j==0:
                    pass
                else:
                    fieldname = fields[j]
                    item[fieldname] = value
                j += 1
            key = row[0]
            items[key] = item
        i += 1
    f.close()
    return items


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
    # eg "ffmpeg -y -i img%05d.png -r 15 a.mp4"
    # cmd = 'ffmpeg -y -i %s -r %d %s' % (filenamePattern, frameRate, outputFilename)
    # cmd = 'ffmpeg -y -i %s -r %d %s > nul' % (filenamePattern, frameRate, outputFilename)
    cmd = 'ffmpeg -y -v 0 -i %s -r %d %s > nul' % (filenamePattern, frameRate, outputFilename)
    print cmd
    os.system(cmd)


def downloadFile(url, filepath):
    "Download a file from a url to a given filepath using curl"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    if os.path.isfile(filepath):
        print "File " + filepath + " already exists"
        return False
    else:
        cmd = "curl -o " + filepath + " " + url
        print cmd
        os.system(cmd)
        return True


def getDownloadUrl(volnumber):
    "Get url to download a volume"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    volprefix = str(volnumber)[0:1] # first digit (=planet number)
    url = config.downloadUrl.format(volprefix, volnumber)
    return url


# def getVolumeTitle(volnumber):
#     "Get name of Voyager volume associated with the volume number"
#     if int(volnumber)==0:
#         return "test"
#     else:
#         return "VGISS_" + str(volnumber)


# def getZipfilepath(volnumber):
#     "Get filepath for zipfile corresponding to a volume number"
#     # eg c:/users/bburns/desktop/voyager/step0_downloads/VGISS_5101.tar.gz
#     sourcefolder = config.downloadFolder
#     url = getDownloadUrl(volnumber)
#     filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
#     zipfilepath = sourcefolder + "/" + filetitle
#     return zipfilepath
    

# #. remove this
# def getUnzippedpath(volnumber):
#     "Get folder path for unzipped volume"
#     # eg c:/users/bburns/desktop/voyager/step1_unzips/VGISS_5101
#     unzipfolder = config.unzipFolder
#     # url = getDownloadUrl(volnumber)
#     # filetitle = getVolumeTitle(volnumber)
#     filetitle = 'VGISS_' + str(volnumber)
#     unzippedpath = unzipfolder + '/' + filetitle
#     return unzippedpath


#. remove this
def getImagespath(volnumber):
    "get folder path for png images"
    # eg c:/users/bburns/desktop/voyager/step2_pngs/VGISS_5101
    imagesfolder = config.imagesFolder
    filetitle = getVolumeTitle(volnumber)
    imagespath = imagesfolder + '/' + filetitle
    return imagespath


#. remove this
def getCenterspath(volnumber):
    "get folder path for centered images"
    # eg c:/users/bburns/desktop/voyager/step3_centered/VGISS_5101
    centersfolder = config.centersFolder
    filetitle = getVolumeTitle(volnumber)
    centerspath = centersfolder + '/' + filetitle
    return centerspath


def unzipFile(zipfile, destfolder):
    "Unzip a file to a destination folder."
    
    # assumes zip file is a .tar or .tar.gz file.
    # doesn't unzip file if destination folder already exists.
    # eg unzipFile('test/unzip_test.tar', 'test/unzip_test')
    
    #. but note - tar file can have a top-level folder, or not -
    # this is assuming that it does, which is why we extract the tarfile
    # to the parent folder of destfolder.
    
    if os.path.isdir(destfolder):
        print "Folder " + destfolder + " already exists - not unzipping"
        return False
    else:
        # tried just building a commandline tar cmd but had issues with windows paths etc
        # this is just as fast anyway
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



