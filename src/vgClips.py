
"""
vg clips command

Build clips associated with target subfolders, eg
> vg clips Jupiter/Voyager1/Io/Narrow

This must be run in an admin console because mklink requires elevated privileges.
"""

#. need to build clips for planet/system titles and all.mp4 titlepage


import csv
import os
import os.path

import config
import lib


import vgCenter
import vgComposite
import vgTitles




def stageFiles(bwOrColor, targetPathParts):
    """Make links from source files (centers or composites) to clip stage folders"""

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

    # open positions.csv file for target angular size info (used to control effective framerate)
    csvPositions, fPositions = lib.openCsvReader(config.positionsdb)

    # iterate through all available images
    reader, f = lib.openCsvReader(config.filesdb)
    for row in reader:

        # read file info
        volume = row[config.filesColVolume]
        fileId = row[config.filesColFileId]
        filter = row[config.filesColFilter]
        system = row[config.filesColPhase]
        craft = row[config.filesColCraft]
        target = row[config.filesColTarget]
        camera = row[config.filesColInstrument]

        # relabel target field if necessary - see db/targets.csv for more info
        target = lib.retarget(targetInfo, fileId, target)

        # does this image match the target path the user specified on the cmdline?
        addImage = True
        if (pathSystem and pathSystem!=system): addImage = False
        if (pathCraft and pathCraft!=craft): addImage = False
        if (pathTarget and pathTarget!=target): addImage = False
        if (pathCamera and pathCamera!=camera): addImage = False
        if target in config.clipsIgnoreTargets: addImage = False
        if addImage:

            # build a key
            targetKey = system + '-' + craft + '-' + target + '-' + camera

            # frameRateConstant = 60 # default
            d = {'Jupiter':1,'Saturn':1,'Uranus':1,'Neptune':1}
            frameRateConstant = d.get(target) or 60
            # get expected angular size
            rowPositions = lib.getJoinRow(csvPositions, config.positionsColFileId, fileId)
            if rowPositions:
                # fraction of frame
                imageFraction = float(rowPositions[config.positionsColImageFraction])
            else:
                imageFraction = 0
            # ncopiesPerImage = int(60 * imageFraction) + 1
            ncopiesPerImage = int(frameRateConstant * imageFraction) + 1
            if ncopiesPerImage > 30: ncopiesPerImage = 30

            # how many copies of this file should we stage?
            # framerateInfoRecord = framerateInfo.get(fileId) # record from framerates.csv
            # if framerateInfoRecord:
            #     # eg ncopies = 3 = 3x slowdown
            #     ncopiesPerImage = int(framerateInfoRecord['nframesPerImage'])
            #     # remember it for future also
            #     # eg key Uranus-Voyager2-Arial-Narrow
            #     key = framerateInfoRecord['planetCraftTargetCamera']
            #     ncopiesPerImageMemory[key] = ncopiesPerImage
            # else:
            #     # lookup where we left off for this target, or 1x speed if not seen before
            #     ncopiesPerImage = ncopiesPerImageMemory.get(targetKey) or 1


            # do we need to center this image?
            doCenter = lib.centerThisImageQ(centeringInfo, targetKey, fileId, target)

            # get image source path
            # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
            # if centering for this image is turned off, let's assume for now that
            # that means we don't want the color image, since it'd be misaligned anyway.
            #. this is true for moons like miranda, e.g.,
            # but for jupiter i like the psychedelic colors
            if doCenter==False:
                imageFilepath = lib.getAdjustedFilepath(volume, fileId, filter)
            elif bwOrColor=='bw':
                imageFilepath = lib.getCenteredFilepath(volume, fileId, filter)
            else:
                imageFilepath = lib.getCompositeFilepath(volume, fileId)

            # i think for more control we'll need something like segments.csv
            # use composite image if available, otherwise the centered or adjusted image
            # if bwOrColor=='color':
            #     imageFilepath = lib.getCompositeFilepath(volume, fileId)
            # if not os.path.isfile(imageFilepath):
            #     imageFilepath = lib.getCenteredFilepath(volume, fileId, filter)
            # if not os.path.isfile(imageFilepath):
            #     imageFilepath = lib.getAdjustedFilepath(volume, fileId, filter)

            # if image file exists, create subfolder and link image
            if os.path.isfile(imageFilepath):

                # get staging subfolder and make sure it exists
                # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/Bw/
                subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                subfolderPlusColor = subfolder + bwOrColor.title() + '/'
                targetFolder = config.clipsStageFolder + subfolderPlusColor
                lib.mkdir_p(targetFolder)

                # get current file number in that folder, or start at 0
                nfile = nfilesInTargetDir.get(targetKey)
                if not nfile: nfile = 0

                # if we haven't seen this subfolder before,
                # add the titlepage image a few times
                # titlepages are created in the previous step, vgBuildTitles
                if config.includeTitles and nfile==0:
                    titleImageFilepath = config.titlesFolder + subfolder + 'title' + \
                                         config.extension
                    # need to get out of the target dir - we're always this deep
                    titleImagePathRelative = '../../../../../../../../' + titleImageFilepath
                    ntitleCopies = config.videoFrameRate * config.titleSecondsToShow
                    lib.makeSymbolicLinks(targetFolder, titleImagePathRelative,
                                          nfile, ntitleCopies)
                    nfile += ntitleCopies

                # print "Volume %s frame: %s              \r" % (volume, imageFilepath),
                print "Volume %s frame: %s x %d           \r" % (volume, imageId, ncopiesPerImage),

                # link to file
                # note: mklink requires admin privileges,
                # so must run this script in an admin console
                # eg imagePath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                # need to get out of the target dir
                imagePathRelative = '../../../../../../../../' + imageFilepath
                lib.makeSymbolicLinks(targetFolder, imagePathRelative, nfile, ncopiesPerImage)

                # increment the file number for the target folder
                nfile += ncopiesPerImage
                nfilesInTargetDir[targetKey] = nfile

    fPositions.close()
    f.close()
    print


def vgClips(bwOrColor, targetPath=None, keepLinks=False):
    "Build bw or color clips associated with the given target path (eg //Io)"
    # eg vgClips('bw', 'Jupiter/Voyager1')

    # note: targetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(targetPath)

    if keepLinks==False:

        # make sure we have the necessary images
        if bwOrColor=='bw':
            lib.loadPreviousStep(targetPathParts, vgCenter.vgCenter)
        else:
            lib.loadPreviousStep(targetPathParts, vgComposite.vgComposite)

        # make sure we have some titles
        vgTitles.vgTitles(targetPath)

        # stage images for ffmpeg
        # lib.rmdir(config.clipsStageFolder)
        # os.rmdir(config.clipsStageFolder)
        import shutil
        shutil.rmtree(config.clipsStageFolder)
        stageFiles(bwOrColor, targetPathParts)

    # build mp4 files from all staged images
    lib.makeVideosFromStagedFiles(config.clipsStageFolder, '../../../../../../',
                                  config.videoFilespec, config.videoFrameRate)


if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # vgClips('bw', 'Jupiter/Voyager1/Io/Narrow')
    # vgClips('bw', '//Triton')
    # vgClips("Neptune")
    # makeLinks()
    makeClipFiles()
    print 'done'


