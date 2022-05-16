# library routines for voyager
# not independent from PyVoyager, but things that might get reused,
# or want kept out of sight.

#. split this up into modules, eg libcsv.py?


import os
import os.path
import shutil
from setuptools import archive_util # for unpack_archive
import errno
import re
import csv # https://python.readthedocs.io/en/v2.7.2/library/csv.html
import shutil
import more_itertools
from datetime import datetime
from dateutil import parser as dtparser


import config



def getCol(row, colnum, default):
    "get a column value from the given row, or the default value if column doesn't exist"
    if len(row)>colnum:
        value = row[colnum]
    else:
        value = default
    return value


def readCsvGroups(filename):
    """
    returns list of groups as gathered from given file, grouped on first column value.
    groups = [group1, group2, ...], with each group = [key,[row1,row2,...]]
    (would return a dictionary but order of groups is sometimes important, eg movies.csv)
    eg
    key,field1,field2
    12,cat,zoey
    12,dog,crayon
    13,lizard,ray
    =>
    [[12,[[12,cat,zoey],[12,dog,crayon]]],[13,[[13,...]]]]
    eg
    group = [12,[[12,cat,zoey],[12,dog,crayon]]]
    so can say
    for group in groups:
        key = group[0]
        rows = group[1]
        for row in rows:
            print row
    """
    csvReader, f = openCsvReader(filename)
    lastKey = ''
    groups = []
    rows = []
    # gather rows for each key into array
    for row in csvReader:
        key = row[0]
        if key != lastKey and lastKey != '':
            group = [lastKey,rows]
            groups.append(group)
            rows = []
        rows.append(row)
        lastKey = key
    group = [lastKey,rows]
    groups.append(group)
    f.close()
    return groups


def makeContentsFile(movieContentsFilepath, filepaths):
    "Make a text file containing a list of mp4 files that will be merged by ffmpeg"
    f = open(movieContentsFilepath, 'w')
    for filepath in filepaths:
        line = "file '../../" + filepath + "'"
        print >> f, line
    f.close()


def concatenateMovies(outputFilepath, inputFilepaths):
    "Concatenate the given mp4 clips into an mp4 movie using ffmpeg"
    # print 'Generating movie', outputFilepath
    movieContentsFilepath = outputFilepath[:-4] + '.txt'
    if inputFilepaths:
        makeContentsFile(movieContentsFilepath, inputFilepaths)
        # now make the movie
        # eg "ffmpeg -y -f concat -i Neptune-Voyager2.txt -c copy Neptune-Voyager2.mp4"
        # cmd = "ffmpeg -y -f concat -i %s -c copy %s" % (movieContentsFilepath, outputFilepath)
        cmd = "ffmpeg -y -loglevel error -f concat -i %s -c copy %s" % (movieContentsFilepath, outputFilepath)
        # print cmd
        os.system(cmd)
    os.remove(movieContentsFilepath)


# def addImages(imageFilepath, targetFolder, ncopies, ntargetDirFiles, targetKey):
def addImages(imageFilepath, targetFolder, ncopies, ntargetDirFiles={}, targetKey=''):
    """
    add symbolic links from imageFilepath to target folder and update nfile count for target.
    imageFilepath should be relative to top PyVoyager folder, e.g. data/step14_pages/Credits.jpg
    used by vgClips and vgMovies.
    """
    nfile = ntargetDirFiles.get(targetKey) or 0
    # need to get out of the target dir back to the top PyVoyager folder
    nlevels = len(targetFolder.split('/')) - 1
    escapePath = '../' * nlevels # eg '../../../../../../../'
    imagePathRelative = escapePath + imageFilepath
    # makeSymbolicLinks(imagePathRelative, targetFolder, nfile, ncopies)
    makeSymbolicLinks(imagePathRelative, targetFolder, ncopies, nfile)
    # increment the file number for the target folder
    nfile += ncopies
    ntargetDirFiles[targetKey] = nfile


def getNCopies(framerateConstantInfo, target, imageFraction, ncopiesMemory, targetKey,
               framerateInfo, fileId):
    """
    How many copies of the given target do we need for clips/movies?
    Bases it on imageFraction, information in targets.csv, framerates.csv, etc.
    Useg by vgClips and vgMovies.
    """

    # ncopies is basically proportional to imageFraction
    # framerateConstantInfoRecord = framerateConstantInfo.get(target)
    framerateConstantInfoRecord = framerateConstantInfo.get(targetKey)
    if framerateConstantInfoRecord:
        frameRateConstant = int(float(framerateConstantInfoRecord['frameRateConstant']))
    else:
        frameRateConstant = config.frameRateConstantDefault
    ncopies = int(frameRateConstant * imageFraction) + 1

    # but don't let it go too slowly
    if ncopies > config.frameRateNCopiesMax:
        ncopies = config.frameRateNCopiesMax

    # check for sticky setting off switch
    framerateInfoRecord = framerateInfo.get(fileId + '-') # eg C1234567-
    if not framerateInfoRecord is None:
        ncopiesMemory.pop(targetKey, None) # remove the sticky setting
        # print 'turned off sticky framerate',fileId

    # check for previous sticky setting override in framerates.csv
    if not ncopiesMemory.get(targetKey) is None:
        ncopies = ncopiesMemory[targetKey]
        # print 'remembering sticky framerate',fileId, ncopies

    # check for 'sticky' override from framerates.csv
    framerateInfoRecord = framerateInfo.get(fileId + '+') # eg C1234567+
    if not framerateInfoRecord is None:
        ncopies = int(framerateInfoRecord['nframes'])
        ncopiesMemory[targetKey] = ncopies # remember it
        # print 'got sticky framerate to remember',fileId,ncopies,ncopiesMemory

    # check for single image override from framerates.csv - temporary setting
    framerateInfoRecord = framerateInfo.get(fileId) # eg C1234567
    if not framerateInfoRecord is None:
        ncopies = int(framerateInfoRecord['nframes'])
        # print 'got single framerate',fileId,ncopies,ncopiesMemory

    return ncopies


def getImageFraction(csvPositions, fileId):
    "look up the imageFraction for the given image in the positions.csv file"
    rowPositions = getJoinRow(csvPositions, config.colPositionsFileId, fileId)
    if rowPositions:
        imageFraction = float(rowPositions[config.colPositionsImageFraction])
    else: # just for rhea and sky
        imageFraction = 0
    return imageFraction


def secondsSince1970(sDatetime, epoch=datetime(1970,1,1)):
    "convert a datetime string to seconds since 1970-01-01"
    # eg "1986-01-18T15:35:10" -> 506446510.0
    dt = dtparser.parse(sDatetime)
    td = dt - epoch
    # return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6
    return td.total_seconds()


#. split into two fns
def loadPreviousStep(targetPathParts, fn):
    """
    load previous build step by determining volumes needed for the given target path.
    calls fn with fn(volume, '', False, False)
    """
    #. this is called by ?

    # what does the user want to focus on?
    pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    # load small db into memory
    retargetingInfo = readCsv(config.dbRetargeting) # remapping listed targets

    # collect volumes needed, call the given fn with those volumes
    volumes = {}
    csvFiles, fFiles = openCsvReader(config.dbFiles)
    for rowFiles in csvFiles:
        volume = rowFiles[config.colFilesVolume]
        fileId = rowFiles[config.colFilesFileId]
        filter = rowFiles[config.colFilesFilter]
        system = rowFiles[config.colFilesSystem]
        craft = rowFiles[config.colFilesCraft]
        target = rowFiles[config.colFilesTarget]
        camera = rowFiles[config.colFilesCamera]

        # relabel target field if necessary
        target = retarget(retargetingInfo, fileId, target)

        addImage = True
        if (pathSystem and pathSystem!=system): addImage = False
        if (pathCraft and pathCraft!=craft): addImage = False
        if (pathTarget and pathTarget!=target): addImage = False
        if (pathCamera and pathCamera!=camera): addImage = False
        # if target in config.clipsIgnoreTargets: addImage = False
        if addImage:
            volumes[volume] = True
    fFiles.close()

    # call the given fn for the needed volumes
    for volume in volumes.keys():
        fn(volume, '', False, False)


def fileContainsString(filename, s):
    "Return True if file contains the given string"
    containsString = False
    f = open(filename,'rt')
    for line in f:
        if s in line:
            containsString = True
            break
    f.close()
    return containsString


def removeLinesFromFile(filename, s):
    "Remove lines containing the given string from the file, unless line is a comment"
    # copy filename to filename_new, leaving out the specified lines
    f = open(filename,'rt')
    f2 = open(filename+'_new','wb')
    for line in f:
        if s in line and line[0]!='#':
            pass
        else:
            f2.write(line)
    f2.close()
    f.close()
    # replace existing file with new version
    os.remove(filename+'_old') # in case still there
    os.rename(filename, filename+'_old')
    os.rename(filename+'_new', filename)
    os.remove(filename+'_old')


def dataLines(lines):
    """
    A filter that excludes comments, blank lines, and the header (first data row) from lines.
    This is a generator - use by wrapping a file or other line source and iterating as normally.
    e.g.
        f = open(filename,'r')
        for line in dataLines(f):
            print line
    """
    i = 0
    for line in lines:
        line = line.strip()
        if line and line[0]!='#':
            if i>0:
                yield line
            i += 1


def centerThisImageQ(imageFraction, centeringInfo, fileId, note, target):
    """
    Should this image be centered? Checks with centering.csv and config.dontCenterTargets.
    Used by vgCenter and vgClips.
    """
    # centeringInfoRecord = centeringInfo.get(targetKey)
    # if centeringInfoRecord:
    #     centeringOff = centeringInfoRecord['centeringOff']
    #     centeringOn = centeringInfoRecord['centeringOn']
    #     doCenter = (fileId < centeringOff) or (fileId > centeringOn)
    # else: # if no info for this target just center it
    #     doCenter = True
    # if target in config.dontCenterTargets: # eg Sky, Dark
    #     doCenter = False
    # return doCenter

    doCenter = (imageFraction < config.imageFractionCenteringThreshold)

    # don't center some targets, eg Sky, Dark
    if target in config.dontCenterTargets: doCenter = False

    # don't center image if has 'search' in note field - satellite/ring searches don't need it
    if 'search' in note.lower(): doCenter = False

    # don't center image if it's listed in centering.csv
    # if fileId in centeringInfo: doCenter = False
    centeringRecord = centeringInfo.get(fileId)
    if centeringRecord:
        doCenter = True if centeringRecord['centerImage']=='y' else False

    return doCenter


def beep():
    os.system('beep')


def getJoinRow(csvReader, joinColumn, joinValue):
    """
    Look for a matching join value in the given csv filereader and return the row, or None.
    This assumes we're walking through the join file in one direction,
    so must be sorted on the join column.
    csvReader iterator must be wrapped with more_itertools.peekable() -
    see http://stackoverflow.com/a/27698681/243392
    And if you use the openCsvReader fn to get the csvReader it will ignore blank lines,
    comments, and the first data line (the header).
    """
    try:
        row = csvReader.peek() # will throw error if eof
        currentValue = row[joinColumn] # if blank row this will throw error also
    except:
        return None
    while currentValue < joinValue:
        try:
            csvReader.next() # pop
            row = csvReader.peek()
            currentValue = row[joinColumn]
        except: # eof
            return None
    if currentValue==joinValue:
        csvReader.next() # pop
        return row
    else:
        return None


def concatFiles(filename1, filename2):
    "concatenate contents of filename2 onto filename1"
    f1 = open(filename1, 'ab')
    f2 = open(filename2, 'rt')
    for line in f2:
        f1.write(line)
    f2.close()
    f1.close()


def retarget(retargetingInfo, fileId, target):
    "get translated target for the given image file and target"
    # retargetingInfo is a db read from retargeting.csv using the readCsv fn
    # see db/retargeting.csv for more info
    retargetingInfoRecord = retargetingInfo.get(fileId)
    if retargetingInfoRecord:
        # make sure old target matches what we have
        if retargetingInfoRecord['oldTarget']==target:
            target = retargetingInfoRecord['newTarget']
        else:
            print 'Warning: retargeting.csv record discrepancy for ' + \
                  fileId,retargetingInfoRecord['oldTarget'],'vs',target
    return target


def openCsvWriter(filename):
    """
    Open a csv writer on the given filename.
    Use like 'writer.writerow(row)'
    """
    f = open(filename, 'wb')
    # writer = csv.writer(f)
    writer = csv.writer(f, lineterminator='\n')
    return writer, f


def openCsvReader(filename):
    """
    Open a csv reader on the given filename.
    Then use like 'for row in reader:'
    Wraps the reader iterator in peekable - see http://stackoverflow.com/a/27698681/243392
    Then can say reader.peek() to just look at the current record, ie don't consume it.
    Returns the reader and the file handle - close when done with f.close().
    """
    f = open(filename, 'rt')
    f = dataLines(f) # ignore comments, blank lines and header row
    reader = more_itertools.peekable(csv.reader(f)) # allows you to peek at the current row
    return reader, f


def cp(src, dst):
    "copy a file to another directory, ignoring any errors"
    try:
        shutil.copy(src, dst)
        return True
    except:
        return False


def getSubfolder(step, volume):
    "get a volume subfolder, eg ('adjust','5101') -> 'data/step03_adjusted/VGISS_5101/'"
    folder = config.folders[step]
    subfolder = folder + 'VGISS_' + volume + '/'
    return subfolder


def getFilepath(step, volume, fileId, filter=None):
    "Get the filepath for the image specified, relative to the main PyVoyager folder."
    folder = config.folders[step] # eg 'adjust' -> 'data/step04_adjusted/'
    suffix = config.suffixes[step] # eg 'adjust' -> '_adjusted'
    subfolder = folder + 'VGISS_' + volume + '/'
    if step=='convert':
        # convert the main processing image type, eg CALIB or RAW
        # eg C1641820_CALIB_GREEN.png
        filetitle = fileId + '_' + config.imageType + '_' + filter.upper() + '.png'
    elif filter:
        # eg C1641820_adjusted_Green.jpg
        filetitle = fileId + suffix + '_' + filter + config.extension
    else:
        # eg C1641820_composite.jpg
        filetitle = fileId + suffix + config.extension
    filepath = subfolder + filetitle
    return filepath


def makeVideosFromStagedFiles(stageFolder, outputFolder):
    """
    Build mp4 videos using ffmpeg on sequentially numbered image files.
    stageFolder contains the sequentially number files, eg data/step10_clips/stage/.
    outputFolder is where the mp4 clips will go.
    """
    # filespec describes the filenames, eg 'foo%04d.png'.
    # frameRate is in fps
    # minFrames is the minimum number of frames needed to build a video.
    print 'Making mp4 clips using ffmpeg'
    for root, dirs, files in os.walk(stageFolder):
        # print root, dirs
        if dirs==[]: # reached the leaf level
            nfiles = len(files)
            # if nfiles >= minFrames:
            if nfiles >= config.clipsMinFrames:
                # root = eg data/step10_clips/stage/Neptune\Voyager2\Triton\Narrow\Bw
                print 'Directory', root
                stageFolderPath = os.path.abspath(root)
                # get target file path relative to staging folder,
                # eg ../../Neptune-Voyager-Triton-Narrow-Bw.mp4
                targetFolder = root[len(stageFolder):] # eg Neptune\Voyager2\Triton\Narrow\Bw
                targetPath = targetFolder.split('\\') # eg ['Neptune','Voyager2',...]
                # videoFiletitle eg 'Neptune-Voyager2-Triton-Narrow-Bw.mp4'
                videoFiletitle = '-'.join(targetPath) + '.mp4'
                # videoFilepath = '../../../../../../' + videoFiletitle
                # videoFilepath = videoFiletitle
                videoFilepath = outputFolder + videoFiletitle
                # imagesToMp4(stageFolderPath, filespec, videoFilepath, frameRate)
                imagesToMp4(stageFolderPath, videoFilepath)


# def makeSymbolicLinks(sourcePath, targetFolder, nfile, ncopies):
def makeSymbolicLinks(sourcePath, targetFolder, ncopies, nfile=0):
    """
    Make ncopies of symbolic links from the source file to the target folder.
    Note: sourcePath must be a relative link, e.g. '../../data/step05_centers/....'
      i.e. it must 'escape' from the target folder to the top-level PyVoyager folder,
      then go down to the file. Just how symbolic links work.
    Make sure targetFolder ends with a slash.
    Numbers files sequentially using config.videoFilespec, starting with number nfile.
    config.videoFilespec is something like "img%05d.jpg".
    """
    # this requires running from an admin console
    for i in range(ncopies):
        n = nfile + i
        targetPath = targetFolder + config.videoFilespec % n # eg 'img00001.png'
        # eg mklink data\step09_clips\Neptune\Voyager2\Neptune\Narrow\Bw\img00001.png
        #   ..\..\..\..\..\..\data\step04_centers\VGISS_8208\centered_C1159959_CALIB_Clear.png
        cmd = 'mklink ' + targetPath + ' ' + sourcePath + ' > nul'
        cmd = cmd.replace('/','\\')
        # print cmd
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
    "parse a string like 5101-5108 or 5104 or 51* to an array of volnum strings"
    # eg getVolumeNumber('5201-5203') => ['5201','5202','5203']

    # handle ranges, eg 8201-8204
    vols = s.split('-')
    if len(vols)==2:
        vols = [int(vol) for vol in vols]
        volrange = range(vols[0],vols[1]+1)
        volrange = [str(vol) for vol in volrange]
        return volrange # eg ['8201','8202','8203','8204']

    # handle invidual volumes or wildcards
    sregex = s.replace('*','.*') # eg '52.*'
    regex = re.compile(sregex)
    vols = []
    svolumes = [str(vol) for vol in config.volumes] # all available volumes
    for svolume in svolumes:
        if re.match(regex, svolume):
            vols.append(svolume)
    return vols


def rm(filepath):
    "remove a file, ignore error (eg if doesn't exist)"
    #. add specific error handlers
    # os.remove(filepath)
    try:
        os.remove(filepath)
    except Exception, e:
        print e
        print e.errno
        # if e.errno==2: # [Error 3] The system cannot find the path specified:
            # pass
        # else:
            # raise


def rmdir(folder):
    "remove a folder and its contents, ignoring errors (eg if it doesn't exist)"
    try:
        shutil.rmtree(folder)
        # shutil.rmtree(folder, ignore_errors=True)
    except Exception, e:
        if e.errno==2: # [Error 3] The system cannot find the path specified
            pass
        elif e.errno==41: # WindowsError: [Error 145] The directory is not empty
            print 'warning: directory could not be removed:',folder
        else:
            print e
            print e.errno
            raise
        # print e.message
        # print exc
        # print exc.errno
        # pass


def targetMatches(targetPathParts, system, craft, target, camera):
    """
    Does the given target path match the given values?
    Where target path part is None, don't filter that value.
    eg if targetPathParts=[None,None,None,None], will always return True.
    """
    # targetPathParts = [s.title() for s in targetPathParts if s]
    matches = True
    if targetPathParts:
        pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts
        if (pathSystem and pathSystem.title()!=system): matches = False
        if (pathCraft and pathCraft.title()!=craft): matches = False
        if (pathTarget and pathTarget.title()!=target): matches = False
        if (pathCamera and pathCamera.title()!=camera): matches = False
    return matches


def parseTargetPath(targetPath):
    """
    Parse a target path, like 'Jupiter/Voyager1' into parts and return as an array.
    Returns [system,craft,target,camera], with None for unspecified parts.
    Then can take apart result with something like -
        pathparts = parseTargetPath(targetPath)
        pathSystem, pathCraft, pathTarget, pathCamera = pathparts
    Returns None if targetPath is empty or None
    # Returns [None,None,None,None] if targetPath is empty or None
    """
    if targetPath:
        pathparts = targetPath.split('/')
        # make sure we have 4 parts, even if blank
        while len(pathparts)<4:
            pathparts.append('')
        # trim,convert blanks to None
        pathparts = [pathpart.strip() for pathpart in pathparts]
        pathparts = [pathpart if len(pathpart)>0 else None for pathpart in pathparts]
        return pathparts
    return None
    # return [None,None,None,None]


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
    # see also mkdir_p
    # rmdir(path) # remove it first
    try:
        os.mkdir(path)
    except Exception as e:
        # already exists
        if e.errno == 5 and os.path.isdir(path):
            pass
        # WindowsError: [Error 183] Cannot create a file when that file already exists
        elif e.errno == 17 and os.path.isdir(path):
            pass
        else:
            print 'mkdir exception'
            print 'e',e
            print 'errno',e.errno
            raise


def mkdir_p(path):
    "Make a directory tree, ignoring any errors (eg if it already exists)"
    # see also mkdir
    try:
        os.makedirs(path)
    except Exception as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        elif e.errno == 13:
            print 'mkdir_p exception'
            print 'e',e
            print 'warning: unable to make directory', path
        else:
            print 'mkdir_p exception'
            print 'e',e
            print 'errno',e.errno
            raise


# def imagesToMp4(stageFolder, filenamePattern, outputFilename, framerate):
def imagesToMp4(stageFolder, outputFilename):
    """
    Convert a sequentially numbered set of images to an mp4 movie.
    stageFolder is the folder containing the sequentially numbered files.
    outputFilename is the mp4 filename, e.g. Neptune-Voyager1.mp4
    """
    # filenamePattern specifies the filenames, e.g. img%05d.jpg
    # framerate is fps
    # outputFilename = outputFilename.replace('mp4','mov') #.
    savedir = os.getcwd()
    os.chdir(stageFolder)
    # print 'cwd',os.getcwd()
    # eg "ffmpeg -y -framerate 25 -i img%05d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4"
    cmd = 'ffmpeg %s -framerate %d -i %s %s %s' % \
          (config.videoFfmpegOptions, config.videoFrameRate,
           config.videoFilespec, config.videoFfmpegOutputOptions,
           outputFilename)
    # print cmd
    os.system(cmd)
    os.chdir(savedir)


def downloadFile(url, folder, filepath):
    "Download a file from a url to a given filepath using curl"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    if os.path.isfile(filepath):
        print "File " + filepath + " already exists"
        return False
    else:
        try:
            os.makedirs(folder)
        except:
            pass
        cmd = "curl -o " + filepath + " " + url
        print cmd
        os.system(cmd)
        return True


def getDownloadUrl(volnum):
    "Get url to download a volume"
    # eg http://pds-rings.seti.org/archives/VGISS_5xxx/VGISS_5101.tar.gz
    volprefix = str(volnum)[0:1] # first digit (=planet number)
    url = config.downloadUrl.format(volprefix, volnum)
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
        # parentfolder = destfolder + ".."
        parentfolder = os.path.normpath(os.path.join(destfolder, os.pardir))
        archive_util.unpack_archive(zipfile, parentfolder)
        return True


if __name__ == '__main__':
    os.chdir('..')

    print getFilepath('inpaint', '5102', 'C1234567')



    # print getDownloadUrl(5101)
    # print getVolumeNumbers('5104')
    # print getVolumeNumbers('5104-5108')
    # print getVolumeNumbers('51*')
    # print getVolumeNumbers('5*')
    # print getVolumeNumbers('*')

    # print getImageIds('c1352753')
    # print getImageIds('c1352753-c1352764')

    # works
    # # test getJoinRow fn
    # data = more_itertools.peekable(iter([[2],[3],[5],[6],[7]]))
    # col = 0
    # row = getJoinRow(data, col, 1)
    # assert row is None
    # assert data.peek()==[2]
    # assert data.peek()==[2]  # doesn't skip ahead
    # row = getJoinRow(data, col, 2)
    # assert row==[2]
    # assert data.peek()==[3]
    # row = getJoinRow(data, col, 4)
    # assert row is None
    # assert data.peek()==[5]
    # row = getJoinRow(data, col, 8)
    # assert row is None
    # row = getJoinRow(data, col, 10)
    # assert row is None


    # print fileContainsString('src/'+__file__, 'fileContainsString')
    # print fileContainsString('src/'+__file__, 'fileContainsString' + 'x')
    # removeLinesFromFile('src/'+__file__,'xxx') # remove this line
    # removeLinesFromFile('src/'+__file__,'yyy'+'vvv') # not this one

    print 'done'

