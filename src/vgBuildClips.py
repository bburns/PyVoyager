
# vg clips command
# build clips associated with target subfolders,
# eg Jupiter/Voyager1/Io/Narrow

# this must be run in an admin console because mklink requires elevated privileges

#. need to build clips for planet/system titles and all.mp4 titlepage
#. and postscript titlepages


import csv
import os
import os.path

import config
import lib

import vgBuildTitles



# includeTitles = True
includeTitles = False


#. parameterize, move to lib
# def makeClipFiles():
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
            lib.pngsToMp4(stageFolderPath, filespec, videoPath, frameRate)
            
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
#             lib.pngsToMp4(stageFolderPath, config.clipFilespec, clipPath, config.clipFrameRate)


def stageFiles(bwOrColor, targetPathParts):
    "Make links from source files (centers or composites) to clip stage folders"

    print 'Making links from source files'

    # what does the user want to focus on?
    pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    # read some small dbs into memory
    targetInfo = lib.readCsv(config.targetsdb) # remapping listed targets
    framerateInfo = lib.readCsv(config.frameratesdb) # change framerates
    centeringInfo = lib.readCsv(config.centeringdb) # turn centering on/off

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
            
            # show progress
            if volume!=lastVolume:
                print 'Volume %s    \r' % volume,
                lastVolume = volume

            system = row[config.filesColPhase]
            craft = row[config.filesColCraft]
            target = row[config.filesColTarget]
            camera = row[config.filesColInstrument]

            # relabel target field if necessary - see db/targets.csv for more info
            targetInfoRecord = targetInfo.get(fileId)
            if targetInfoRecord:
                # make sure old target matches what we have
                if targetInfoRecord['oldTarget']==target:
                    target = targetInfoRecord['newTarget']

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

                # get image source path
                # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                #. make this a fn - duplicated elsewhere
                centeringInfoRecord = centeringInfo.get(planetCraftTargetCamera)
                if centeringInfoRecord:
                    centeringOff = centeringInfoRecord['centeringOff']
                    centeringOn = centeringInfoRecord['centeringOn']
                    docenter = fileId<centeringOff or fileId>centeringOn
                else: # if no info for this target just center it
                    docenter = True
                    
                # if centering for this image is turned off, let's assume for now that
                # that means we don't want the color image, since it'd be misaligned anyway.
                if docenter==False:
                    pngSubfolder = config.adjustmentsFolder + 'VGISS_' + volume + '/'
                    pngfilename = config.adjustmentsPrefix + fileId + '_' + \
                                  config.imageType + '_' + filter + '.png'
                elif bwOrColor=='bw':
                    pngSubfolder = config.centersFolder + 'VGISS_' + volume + '/'
                    pngfilename = config.centersPrefix + fileId + '_' + \
                                  config.imageType + '_' + filter + '.png'
                else:
                    pngSubfolder = config.compositesFolder + 'VGISS_' + volume + '/'
                    pngfilename = config.compositesPrefix + fileId + '.png'
                pngpath = pngSubfolder + pngfilename

                # if image file exists, create subfolder and link image
                if os.path.isfile(pngpath):

                    # get staging subfolder and make sure it exists
                    # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/Bw/
                    subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                    subfolderPlusColor = subfolder + bwOrColor.title() + '/'
                    targetfolder = config.clipsStageFolder + subfolderPlusColor
                    lib.mkdir_p(targetfolder)

                    # get current file number in that folder, or start at 0
                    nfile = nfilesInTargetDir.get(planetCraftTargetCamera)
                    if not nfile: nfile = 0

                    # if we haven't seen this subfolder before, add the titlepage image a few times.
                    # titlepages are created in the previous step, vgBuildTitles.
                    if includeTitles and nfile==0:
                        titleimagefilepath = config.titlesFolder + subfolder + 'title.png'
                        # need to get out of the target dir - we're always this deep
                        titleimagepathrelative = '../../../../../../../../' + titleimagefilepath
                        ntitlecopies = config.clipFramesForTitles
                        lib.makeSymbolicLinks(targetfolder, titleimagepathrelative,
                                              nfile, ntitlecopies)
                        nfile += ntitlecopies

                    # link to file
                    # note: mklink requires admin privileges,
                    # so must run this script in an admin console
                    # eg pngpath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                    # need to get out of the target dir
                    pngpathrelative = '../../../../../../../../' + pngpath
                    lib.makeSymbolicLinks(targetfolder, pngpathrelative, nfile, ncopiesPerImage)
                    print "Frame %d: %s      \r" % (nfile, pngpathrelative),

                    # increment the file number for the target folder
                    nfile += ncopiesPerImage
                    nfilesInTargetDir[planetCraftTargetCamera] = nfile

        i += 1

    f.close()
    print


def buildClips(bwOrColor, targetPath=None):
    "Build bw or color clips associated with the given target path (eg //Io)"
    # eg buildClips('bw', 'Jupiter/Voyager1')

    # note: targetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(targetPath)

    # make sure we have some titles
    vgBuildTitles.buildTitles(targetPath)

    # stage images for ffmpeg
    lib.rmdir(config.clipsStageFolder)
    stageFiles(bwOrColor, targetPathParts)

    # build mp4 files from all staged images
    # makeClipFiles()
    lib.makeVideosFromStagedFiles(config.clipsStageFolder, '../../../../../../',
                                  config.clipFilespec, config.clipFrameRate)
    

if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # buildClips('bw', 'Jupiter/Voyager1/Io/Narrow')
    # buildClips('bw', '//Triton')
    # buildClips("Neptune")
    # makeLinks()
    makeClipFiles()
    print 'done'


