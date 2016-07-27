
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




def stageFiles(bwOrColor, targetPathParts):
    "Make links from source files (centers or composites) to clip stage folders"

    print 'Making links from source files'

    # what does the user want to focus on?
    pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    # read some small dbs into memory
    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets
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

            #. make lib fn
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
            if target in config.clipsIgnoreTargets: addImage = False
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
                    doCenter = (fileId < centeringOff) or (fileId > centeringOn)
                else: # if no info for this target just center it
                    doCenter = True

                # if centering for this image is turned off, let's assume for now that
                # that means we don't want the color image, since it'd be misaligned anyway.
                if doCenter==False:
                    # imageSubfolder = config.adjustmentsFolder + 'VGISS_' + volume + '/'
                    # imageFilename = lib.getAdjustedFilename(fileId, filter)
                    imageFilepath = lib.getAdjustedFilepath(volume, fileId, filter)
                elif bwOrColor=='bw':
                    # imageSubfolder = config.centersFolder + 'VGISS_' + volume + '/'
                    # imageFilename = lib.getCenteredFilename(fileId, filter)
                    imageFilepath = lib.getCenteredFilepath(volume, fileId, filter)
                else:
                    # imageSubfolder = config.compositesFolder + 'VGISS_' + volume + '/'
                    # imageFilename = lib.getCompositeFilename(fileId, filter)
                    imageFilepath = lib.getCompositeFilepath(volume, fileId, filter)
                # pngPath = pngSubfolder + pngFilename
                # imagePath = imageSubfolder + imageFilename

                # if image file exists, create subfolder and link image
                # if os.path.isfile(pngPath):
                if os.path.isfile(imageFilepath):

                    # get staging subfolder and make sure it exists
                    # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/Bw/
                    subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                    subfolderPlusColor = subfolder + bwOrColor.title() + '/'
                    targetFolder = config.clipsStageFolder + subfolderPlusColor
                    lib.mkdir_p(targetFolder)

                    # get current file number in that folder, or start at 0
                    nfile = nfilesInTargetDir.get(planetCraftTargetCamera)
                    if not nfile: nfile = 0

                    # if we haven't seen this subfolder before, add the titlepage image a few times.
                    # titlepages are created in the previous step, vgBuildTitles.
                    if config.includeTitles and nfile==0:
                        titleImageFilepath = config.titlesFolder + subfolder + 'title.png'
                        # need to get out of the target dir - we're always this deep
                        titleImagePathRelative = '../../../../../../../../' + titleImageFilepath
                        ntitleCopies = config.clipFramesForTitles
                        lib.makeSymbolicLinks(targetFolder, titleImagePathRelative,
                                              nfile, ntitleCopies)
                        nfile += ntitleCopies

                    # link to file
                    # note: mklink requires admin privileges,
                    # so must run this script in an admin console
                    # eg imagePath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                    # need to get out of the target dir
                    imagePathRelative = '../../../../../../../../' + imageFilepath
                    lib.makeSymbolicLinks(targetFolder, imagePathRelative, nfile, ncopiesPerImage)
                    print "Frame %d: %s              \r" % (nfile, imageFilepath),

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
    lib.makeVideosFromStagedFiles(config.clipsStageFolder, '../../../../../../',
                                  config.videoFilespec, config.videoFrameRate)


if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # buildClips('bw', 'Jupiter/Voyager1/Io/Narrow')
    # buildClips('bw', '//Triton')
    # buildClips("Neptune")
    # makeLinks()
    makeClipFiles()
    print 'done'


