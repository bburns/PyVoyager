
# build clips associated with target subfolders,
# eg Jupiter/Voyager1/Io/Narrow

# this must be run in an admin console because mklink requires elevated privileges


import csv
import os
import os.path

import config
import lib

import vgBuildTitles



def makeClipFiles():
    "build mp4 clips using ffmpeg on sequentially numbered image files"
    print 'make mp4 clips using ffmpeg'
    # folder = config.clipsFolder
    folder = config.clipsStageFolder # eg data/step09_clips/stage/
    # print folder
    for root, dirs, files in os.walk(folder):
        # print root, dirs
        if dirs==[]: # reached the leaf level
            print 'directory', root # eg data/step09_clips/stage/Neptune\Voyager2\Triton\Narrow\Bw
            stageFolder = os.path.abspath(root)
            # get target file path relative to staging folder,
            # eg ../../Neptune-Voyager-Triton-Narrow-Bw.mp4
            targetFolder = root[len(folder):] # eg Neptune\Voyager2\Triton\Narrow\Bw
            targetPath = targetFolder.split('\\') # eg ['Neptune','Voyager2',...]
            clipTitle = '-'.join(targetPath) + '.mp4' # eg 'Neptune-Voyager2-Triton-Narrow-Bw.mp4'
            clipPath = '../../../../../../' + clipTitle
            lib.pngsToMp4(stageFolder, config.clipFilespec, clipPath, config.clipFrameRate)


def makeLink(targetFolder, sourcePath, nfile, ncopies):
    "make ncopies of symbolic link from the source to the target file, starting with number nfile"
    # this requires running vg from an admin console
    for i in range(ncopies):
        n = nfile + i
        targetPath2 = targetFolder + config.clipFilespec % n # eg 'img00001.png'
        # eg mklink data\step09_clips\Neptune\Voyager2\Neptune\Narrow\Bw\img00001.png
        #   ..\..\..\..\..\..\data\step04_centers\VGISS_8208\centered_C1159959_CALIB_Clear.png > nul
        cmd = 'mklink ' + targetPath2 + ' ' + sourcePath + ' > nul'
        cmd = cmd.replace('/','\\')
        os.system(cmd)


def makeLinks(bwOrColor, targetPathParts):
    "make links from source files (centers or composites) to clip stage folders"

    print 'making links from source files'

    # what does the user want to focus on?
    pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    # read some small dbs into memory
    targetInfo = lib.readCsv('db/targets.csv') # remapping listed targets
    framerateInfo = lib.readCsv('db/framerates.csv') # change framerates

    # keep track of number of files in each target subfolder,
    # so we can number files appropriately and know when to add titles
    nfilesInTargetDir = {}

    # how many times should we duplicate the images?
    ncopiesPerImage = 1 # default
    ncopiesPerImageMemory = {} # keyed on planet-spacecraft-target-camera

    # iterate through all available images
    f = open(config.filesdb, 'rt')
    i = 0
    lastVolume=''
    reader = csv.reader(f)
    for row in reader:
        if row==[] or row[0][0]=="#": continue # ignore blank lines and comments
        if i==0: fields = row
        else:
            # read file info
            volume = row[config.filesColVolume]
            fileId = row[config.filesColFileId]
            filter = row[config.filesColFilter]

            # get image source path
            # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
            if bwOrColor=='bw':
                pngSubfolder = config.centersFolder + 'VGISS_' + volume + '/'
                pngfilename = config.centersPrefix + fileId + '_' + \
                              config.imageType + '_' + filter + '.png'
            else:
                pngSubfolder = config.compositesFolder + 'VGISS_' + volume + '/'
                pngfilename = config.compositesPrefix + fileId + '.png'
            pngpath = pngSubfolder + pngfilename

            # if image file exists, create subfolder and link image
            if os.path.isfile(pngpath):

                # show progress
                if volume!=lastVolume:
                    print 'volume', volume
                    # print 'volume %s\r' % volume
                    lastVolume = volume

                system = row[config.filesColPhase]
                craft = row[config.filesColCraft]
                target = row[config.filesColTarget]
                camera = row[config.filesColInstrument]

                # relabel target field if necessary - see db/multitargetImages.csv for more info
                targetInfo = multitargetInfo.get(fileId)
                if targetInfo:
                    # make sure old target matches what we have
                    if targetInfo['oldTarget']==target:
                        target = targetInfo['newTarget']

                # does this image match the target path the user specified on the cmdline?
                addImage = True
                if (pathSystem and pathSystem!=system): addImage = False
                if (pathCraft and pathCraft!=craft): addImage = False
                if (pathTarget and pathTarget!=target): addImage = False
                if (pathCamera and pathCamera!=camera): addImage = False
                if addImage:

                    # build a key
                    planetCraftTargetCamera = system + '-' + craft + '-' + target + '-' + camera

                    # how many copies of this file should we stage?
                    framerateInfoRecord = framerateInfo.get(fileId) # record from framerates.csv
                    if framerateInfoRecord:
                        # eg ncopies = 3 = 3x slowdown
                        ncopiesPerImage = int(framerateInfoRecord['nframesPerImage'])
                        # remember it for future also
                        # eg key Uranus-Voyager2-Arial-Narrow
                        key = framerateInfoRecord['planetCraftTargetCamera']
                        ncopiesPerImageMemory[key] = ncopiesPerImage
                    else:
                        # lookup where we left off for this target, or 1x speed if not seen before
                        ncopiesPerImage = ncopiesPerImageMemory.get(planetCraftTargetCamera) or 1

                    # get staging subfolder and make sure it exists
                    # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/Bw/
                    subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                    subfolderPlusColor = subfolder + bwOrColor.title() + '/'
                    targetfolder = config.clipstageFolder + subfolderPlusColor
                    lib.mkdir_p(targetfolder)

                    # get current file number in that folder, or start at 0
                    nfile = nfilesInTargetDir.get(planetCraftTargetCamera)
                    if not nfile: nfile = 0

                    # if we haven't seen this subfolder before, add the titlepage image a few times.
                    # titlepages are created in the previous step, vgBuildTitles.
                    if nfile==0:
                        titleimagefilepath = config.titlesFolder + subfolder + 'title.png'
                        # need to get out of the target dir - we're always this deep
                        titleimagepathrelative = '../../../../../../../../' + titleimagefilepath
                        ntitlecopies = config.clipFramesForTitles
                        makeLink(targetfolder, titleimagepathrelative, nfile, ntitlecopies)
                        nfile += ntitlecopies

                    # link to file
                    # note: mklink requires admin privileges,
                    # so must run this script in an admin console
                    # eg pngpath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                    # need to get out of the target dir
                    pngpathrelative = '../../../../../../../../' + pngpath
                    makeLink(targetfolder, pngpathrelative, nfile, ncopiesPerImage)

                    # increment the file number for the target folder
                    nfile += ncopiesPerImage
                    nfilesInTargetDir[planetCraftTargetCamera] = nfile

        i += 1

    f.close()


def buildClips(bwOrColor, targetPath=None):
    "build bw or color clips associated with the given target path (eg //Io)"
    # eg buildClips('bw', 'Jupiter/Voyager1')

    # note: targetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(targetPath)

    # make sure we have some titles
    vgBuildTitles.buildTitles(targetPath)

    # stage images
    lib.rmdir(config.clipsStageFolder)
    makeLinks(bwOrColor, targetPathParts)

    # build mp4 files from all staged images
    makeClipFiles()


if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # buildClips('bw', 'Jupiter/Voyager1/Io/Narrow')
    # buildClips('bw', '//Triton')
    # buildClips("Neptune")
    # makeLinks()
    makeClipFiles()
    print 'done'


