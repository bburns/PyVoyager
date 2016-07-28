
# library routines for voyager


import os # for system, mkdir, mkdirs
import os.path # for isfile
import shutil # for rmtree
from setuptools import archive_util # for unpack_archive
import errno
import re # for findall
import csv
import shutil

# for makeTitlePage
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


#. should pass any constants into functions (ideally)
import config



def getJoinRow(csvReader, joinColumn, joinValue, lastJoinValue):
    "look for a matching join value in the given csv filereader and return the row, or None"
    # this assumes we're walking through the join file in one direction
    # so must be sorted on the join column
    row = None
    while lastJoinValue < joinValue:
        try:
            row = csvReader.next()
        except:
            row = None
            break
        lastJoinValue = row[joinColumn]
    return row, lastJoinValue


def concatFiles(filename1, filename2):
    "concatenate contents of filename2 onto filename1"
    f1 = open(filename1, 'ab')
    f2 = open(filename2, 'rt')
    for line in f2:
        f1.write(line)
    f2.close()
    f1.close()


def retarget(targetInfo, fileId, target):
    "get translated target for the given image file and target"
    # targetInfo is a db read from retargeting.csv using the readCsv fn
    # see db/retargeting.csv for more info
    targetInfoRecord = targetInfo.get(fileId)
    if targetInfoRecord:
        # make sure old target matches what we have
        if targetInfoRecord['oldTarget']==target:
            target = targetInfoRecord['newTarget']
        else:
            print 'Warning: retargeting.csv record discrepancy for ' + fileId
    return target


def openCsvWriter(filename):
    "open a csv writer on the given filename"
    # use like 'writer.writerow(row)'
    f = open(filename, 'wb')
    writer = csv.writer(f)
    return writer, f


def openCsvReader(filename):
    "open a csv reader on the given filename"
    # use like 'for row in reader:'
    f = open(filename, 'rt')
    reader = csv.reader(f)
    return reader, f


def cp(src, dst):
    "copy a file to another directory, ignoring any errors"
    try:
        shutil.copy(src, dst)
    except:
        pass


#. might only need the Filepath variants
def getAdjustedFilename(fileId, filter):
    "get the filename for the adjusted image specified"
    filename = fileId + config.adjustmentsSuffix + '_' + filter + config.extension
    return filename

def getCenteredFilename(fileId, filter):
    "get the filename for the centered image specified"
    filename = fileId + config.centersSuffix + '_' + filter + config.extension
    return filename

def getCompositeFilename(fileId, filter):
    "get the filename for the composite image specified"
    filename = fileId + config.compositesSuffix + config.extension
    return filename


def getAdjustedFilepath(volume, fileId, filter):
    "get the filepath for the adjusted image specified"
    folder = config.adjustmentsFolder + 'VGISS_' + volume + '/'
    filetitle = fileId + config.adjustmentsSuffix + '_' + filter + config.extension
    filepath = folder + filetitle
    return filepath

def getCenteredFilepath(volume, fileId, filter):
    "get the filepath for the centered image specified"
    folder = config.centersFolder + 'VGISS_' + volume + '/'
    filetitle = fileId + config.centersSuffix + '_' + filter + config.extension
    filepath = folder + filetitle
    return filepath

def getCompositeFilepath(volume, fileId, filter):
    "get the filepath for the composite image specified"
    folder = config.compositesFolder + 'VGISS_' + volume + '/'
    filetitle = fileId + config.compositesSuffix + config.extension
    filepath = folder + filetitle
    return filepath


def makeVideosFromStagedFiles(stageFolder, outputFolder, filespec, frameRate):
    "Build mp4 videos using ffmpeg on sequentially numbered image files"
    # eg data/step09_clips/stage/
    print 'Making mp4 clips using ffmpeg'
    for root, dirs, files in os.walk(stageFolder):
        # print root, dirs
        if dirs==[]: # reached the leaf level
            print 'Directory', root # eg data/step09_clips/stage/Neptune\Voyager2\Triton\Narrow\Bw
            stageFolderPath = os.path.abspath(root)
            # get target file path relative to staging folder,
            # eg ../../Neptune-Voyager-Triton-Narrow-Bw.mp4
            targetFolder = root[len(stageFolder):] # eg Neptune\Voyager2\Triton\Narrow\Bw
            targetPath = targetFolder.split('\\') # eg ['Neptune','Voyager2',...]
            videoTitle = '-'.join(targetPath) + '.mp4' # eg 'Neptune-Voyager2-Triton-Narrow-Bw.mp4'
            # videoPath = '../../../../../../' + videoTitle
            videoPath = outputFolder + videoTitle
            imagesToMp4(stageFolderPath, filespec, videoPath, frameRate)

# def makeClipFiles():
#     "Build mp4 clips using ffmpeg on sequentially numbered image files"

#     print 'Making mp4 clips using ffmpeg'
#     stageFolder = config.clipsStageFolder # eg data/step09_clips/stage/
#     # print folder
#     for root, dirs, files in os.walk(stageFolder):
#         # print root, dirs
#         if dirs==[]: # reached the leaf level
#             print 'Directory', root # eg data/step09_clips/stage/Neptune\Voyager2\Triton\Narrow\Bw
#             stageFolderPath = os.path.abspath(root)
#             # get target file path relative to staging folder,
#             # eg ../../Neptune-Voyager-Triton-Narrow-Bw.mp4
#             targetFolder = root[len(stageFolder):] # eg Neptune\Voyager2\Triton\Narrow\Bw
#             targetPath = targetFolder.split('\\') # eg ['Neptune','Voyager2',...]
#             clipTitle = '-'.join(targetPath) + '.mp4' # eg 'Neptune-Voyager2-Triton-Narrow-Bw.mp4'
#             clipPath = '../../../../../../' + clipTitle
#             lib.imagesToMp4(stageFolderPath, config.clipFilespec, clipPath, config.clipFrameRate)



def makeSymbolicLinks(targetFolder, sourcePath, nfile, ncopies):
    "Make ncopies of symbolic link from the source to the target file, starting with number nfile"
    # this requires running from an admin console
    for i in range(ncopies):
        n = nfile + i
        targetPath2 = targetFolder + config.videoFilespec % n # eg 'img00001.png'
        # eg mklink data\step09_clips\Neptune\Voyager2\Neptune\Narrow\Bw\img00001.png
        #   ..\..\..\..\..\..\data\step04_centers\VGISS_8208\centered_C1159959_CALIB_Clear.png > nul
        cmd = 'mklink ' + targetPath2 + ' ' + sourcePath + ' > nul'
        cmd = cmd.replace('/','\\')
        os.system(cmd)



def getImageIds(s):
    "parse a string like c1353371-c1353380 or c1353775 to an array of image ids"
    # eg getImageIds('c1353775-c1353776') => ['C1353775','C1353776']

    # handle ranges, eg c1353775-c1353776
    imageIds = s.split('-')
    if len(imageIds)==2:
        imageNums = [int(imageId[1:]) for imageId in imageIds]
        imageRange = range(imageNums[0],imageNums[1]+1)
        imageRange = ['C' + str(imageNum) for imageNum in imageRange]
        return imageRange # eg ['C1353775','C1353776']

    # handle invidual imageId
    imageId = 'C' + s[1:]
    return [imageId]


def getVolumeNumbers(s):
    "parse a string like 5101-5108 or 5104 or 51* to an array of volnum integers"
    # eg getVolumeNumber('5201-5203') => [5201,5202,5203]

    # handle ranges, eg 8201-8204
    vols = s.split('-')
    if len(vols)==2:
        vols = [int(vol) for vol in vols]
        volrange = range(vols[0],vols[1]+1)
        return volrange # eg [8201,8202,8203,8204]

    # handle invidual volumes or wildcards
    sregex = s.replace('*','.*') # eg '52.*'
    regex = re.compile(sregex)
    vols = []
    svolumes = [str(vol) for vol in config.volumes] # all available volumes
    for svolume in svolumes:
        if re.match(regex, svolume):
            vols.append(int(svolume))
    return vols


def rm(filepath):
    "remove a file, ignore error (eg if doesn't exist)"
    try:
        os.remove(filepath)
    except:
        pass


def rmdir(folder):
    "remove a folder and its contents, ignoring errors (eg if it doesn't exist)"
    try:
        shutil.rmtree(folder)
    except:
        pass


def parseTargetPath(targetPath):
    "parse a target path, like 'Jupiter/Voyager1' into parts and return as an array [system,craft,target,camera], with None for unspecified parts."
    # then can take apart result with something like -
    # pathparts = parseTargetPath(targetPath)
    # pathSystem, pathCraft, pathTarget, pathCamera = pathparts
    pathparts = targetPath.split('/')
    # make sure we have 4 parts, even if blank
    while len(pathparts)<4:
        pathparts.append('')
    # trim,convert blanks to None
    pathparts = [pathpart.strip() for pathpart in pathparts]
    pathparts = [pathpart if len(pathpart)>0 else None for pathpart in pathparts]
    return pathparts


def makeTitlePage(title, subtitle1='', subtitle2='', subtitle3=''):
    "draw a title page, return a PIL image"

    font = ImageFont.truetype(config.titleFont, config.titleFontsize)

    imgsize = (800,800)
    bgcolor = (0,0,0)
    fgcolor = (200,200,200)
    pos = (200,300)

    img = Image.new("RGBA", imgsize, bgcolor)
    draw = ImageDraw.Draw(img)

    s = title
    draw.text(pos, s, fgcolor, font=font)
    w,h = font.getsize(s)
    # print w,h # 207,53

    pos = (pos[0],pos[1]+h*1.5)
    s = subtitle1
    fgcolor = (120,120,120)
    draw.text(pos, s, fgcolor, font=font)

    pos = (pos[0],pos[1]+h)
    s = subtitle2
    draw.text(pos, s, fgcolor, font=font)

    pos = (pos[0],pos[1]+h)
    s = subtitle3
    draw.text(pos, s, fgcolor, font=font)

    draw = ImageDraw.Draw(img)
    # img.save("a_test.png")
    return img



def readCsv(filename):
    "Read a csv file into a dict of dicts. First column is key. Use on small files only!"
    # comments or blank lines are skipped
    # not all values need to be filled in
    f = open(filename, 'rt')
    i = 0
    items = {}
    reader = csv.reader(f)
    for row in reader:
        if row==[] or row[0][0]=='#': continue # skip blank lines and comments
        if i==0: fields = row
        else:
            col = 0
            item = {}
            for value in row:
                if col==0:
                    pass
                else:
                    fieldname = fields[col]
                    item[fieldname] = value
                col += 1
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


def imagesToMp4(stageFolder, filenamePattern, outputFilename, frameRate):
    "Convert a sequentially numbered set of images to an mp4 movie"
    # stageFolder is the folder containing the sequentially numbered files
    savedir = os.getcwd()
    os.chdir(stageFolder)
    # eg "ffmpeg -y -i img%05d.png -r 15 a.mp4"
    # cmd = 'ffmpeg -y %s -r 1 -i %s -r %d %s' % (config.movieFfmpegOptions, filenamePattern, frameRate, outputFilename)
    # cmd = 'ffmpeg -y %s -framerate %d -i %s -r %d %s' % (config.movieFfmpegOptions, frameRate, filenamePattern, frameRate, outputFilename)
    # cmd = 'ffmpeg %s -framerate 1 -i %s -r %d %s' % (config.movieFfmpegOptions, filenamePattern, frameRate, outputFilename)
    cmd = 'ffmpeg %s -framerate %d -i %s %s %s' % (config.videoFfmpegOptions, frameRate, filenamePattern, config.videoFfmpegOutputOptions, outputFilename)
    print cmd
    os.system(cmd)
    os.chdir(savedir)


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



def unzipFile(zipfile, destfolder, overwrite=False):
    "Unzip a file to a destination folder."
    # eg unzipFile('test/unzip_test.tar', 'test/unzip_test/')

    # assumes zip file is a .tar or .tar.gz file.
    # by default doesn't unzip file if destination folder already exists.

    #. but note - tar file can have a top-level folder, or not -
    # this is assuming that it does, which is why we actually extract the tarfile
    # to the parent folder of destfolder.

    if os.path.isdir(destfolder) and overwrite==False:
        print "Folder " + destfolder + " already exists - not unzipping"
        return False
    else:
        rmdir(destfolder)
        # tried just building a commandline tar cmd but had issues with windows paths etc
        # this is just as fast anyway
        parentfolder = destfolder + "/.."
        archive_util.unpack_archive(zipfile, parentfolder)
        return True



if __name__ == '__main__':
    os.chdir('..')
    # print getDownloadUrl(5101)
    # print getVolumeNumbers('5104')
    # print getVolumeNumbers('5104-5108')
    # print getVolumeNumbers('51*')
    # print getVolumeNumbers('5*')
    # print getVolumeNumbers('*')
    print getImageIds('c1352753')
    print getImageIds('c1352753-c1352764')
    print 'done'

