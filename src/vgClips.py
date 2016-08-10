
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

# import vgCenter
import vgComposite
import vgTitles



def getNCopies(targetInfo, target, imageFraction, ncopiesMemory, targetKey,
               framerateInfo, fileId):
    """
    how many copies of the given target do we need?
    uses imageFraction, information in targets.csv, framerates.csv, etc.
    """

    # ncopies is proportional to imageFraction
    targetInfoRecord = targetInfo.get(target)
    if targetInfoRecord:
        frameRateConstant = int(float(targetInfoRecord['frameRateConstant']))
    else:
        frameRateConstant = config.clipsDefaultFrameRateConstant
    ncopies = int(frameRateConstant * imageFraction) + 1

    # don't let it go too slowly
    if ncopies > config.clipsMaxFrameRateConstant:
        ncopies = config.clipsMaxFrameRateConstant

    # check for previous sticky setting override in framerates.csv
    if not ncopiesMemory.get(targetKey) is None:
        ncopies = ncopiesMemory[targetKey]
        # print 'remembering sticky framerate',fileId, ncopies

    # check for 'sticky' override from framerates.csv
    framerateInfoRecord = framerateInfo.get(fileId + '+')
    if not framerateInfoRecord is None:
        ncopies = int(framerateInfoRecord['nframesPerImage'])
        ncopiesMemory[targetKey] = ncopies # remember it
        # print 'got sticky framerate to remember',fileId,ncopies,ncopiesMemory

    # check for single image override from framerates.csv
    framerateInfoRecord = framerateInfo.get(fileId)
    if not framerateInfoRecord is None:
        ncopies = int(framerateInfoRecord['nframesPerImage'])
        # ncopiesMemory[targetKey] = None # reset the sticky setting
        ncopiesMemory.pop(targetKey, None) # remove the sticky setting
        # print 'got single framerate',fileId,ncopies,ncopiesMemory

    return ncopies


# def stageFiles(bwOrColor, targetPathParts):
# def stageFiles(targetPathParts):
def stageFiles(volnums, targetPathParts):
    """
    Make links from source files (centers or composites) to clip stage folders.
    """

    print 'Making links from source files'

    print volnums, targetPathParts

    # what does the user want to focus on?
    # pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    # read some small dbs into memory
    retargetingInfo = lib.readCsv(config.retargetingdb) # remapping listed targets
    targetInfo = lib.readCsv(config.targetdb) # change framerates per target
    framerateInfo = lib.readCsv(config.frameratesdb) # change framerates per image
    centeringInfo = lib.readCsv(config.centeringdb) # turn centering on/off

    # keep track of number of files in each target subfolder,
    # so we can number files appropriately and know when to add titles
    nfilesInTargetDir = {}

    # how many times should we duplicate the images?
    ncopies = 1 # default
    ncopiesMemory = {} # keyed on planet-spacecraft-target-camera

    # open positions.csv file for target angular size info (used to control effective framerate)
    csvPositions, fPositions = lib.openCsvReader(config.positionsdb)

    # open additions.csv for additional images to insert into sequence
    csvAdditions, fAdditions = lib.openCsvReader(config.additionsdb)

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)
    for row in csvFiles:

        # get file info
        volume = row[config.filesColVolume]
        fileId = row[config.filesColFileId]
        filter = row[config.filesColFilter]
        system = row[config.filesColPhase]
        craft = row[config.filesColCraft]
        target = row[config.filesColTarget]
        camera = row[config.filesColInstrument]

        # relabel target field if necessary - see db/targets.csv for more info
        target = lib.retarget(retargetingInfo, fileId, target)

        # get expected angular size (as fraction of frame)
        rowPositions = lib.getJoinRow(csvPositions, config.positionsColFileId, fileId)
        if rowPositions:
            imageFraction = float(rowPositions[config.positionsColImageFraction])
        else:
            imageFraction = 0

        # build a key
        targetKey = system + '-' + craft + '-' + target + '-' + camera

        # how many copies of this image do we want?
        # note: we need to do this even if we don't add this image,
        # because need to keep track of sticky overrides from framerates.csv.
        ncopies = getNCopies(targetInfo, target, imageFraction, ncopiesMemory,
                             targetKey, framerateInfo, fileId)

        # does this image match the target path the user specified on the cmdline?
        addImage = False
        # if volume in volnums: addImage = True
        # if lib.targetMatches(targetPathParts, system, craft, target, camera): addImage = True
        if (volume in volnums) and \
           lib.targetMatches(targetPathParts, system, craft, target, camera):
            addImage = True
        if target in config.clipsIgnoreTargets: addImage = False
        if addImage and ncopies > 0:

            # do we need to center this image?
            # this is out of date - just base it on whether centered file exists
            # doCenter = lib.centerThisImageQ(centeringInfo, targetKey, fileId, target)

            # get image source path
            # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
            # if centering for this image is turned off, let's assume for now that
            # that means we don't want the color image, since it'd be misaligned anyway.
            #. this is true for moons like miranda, e.g.,
            # but for jupiter i like the psychedelic colors
            # if doCenter==False:
            #     imageFilepath = lib.getAdjustedFilepath(volume, fileId, filter)
            # elif bwOrColor=='bw':
            #     imageFilepath = lib.getCenteredFilepath(volume, fileId, filter)
            # else:
            #     imageFilepath = lib.getCompositeFilepath(volume, fileId)

            # use composite image if available, otherwise the centered or adjusted image
            # if bwOrColor=='color':
                # imageFilepath = lib.getCompositeFilepath(volume, fileId)
            # elif bwOrColor=='bw':
                # imageFilepath = lib.getCenteredFilepath(volume, fileId, filter)
                # if not os.path.isfile(imageFilepath):
                    # imageFilepath = lib.getAdjustedFilepath(volume, fileId, filter)
            imageFilepath = lib.getCompositeFilepath(volume, fileId)

            # if image file exists, create subfolder and link image
            if os.path.isfile(imageFilepath):

                # get staging subfolder and make sure it exists
                # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/Bw/
                subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                # subfolderPlusColor = subfolder + bwOrColor.title() + '/'
                # targetFolder = config.clipsStageFolder + subfolderPlusColor
                targetFolder = config.clipsStageFolder + subfolder
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

                print "Volume %s frame: %s x %d           \r" % (volume, fileId, ncopies),
                # print "Volume %s frame: %s x %d           " % (volume, fileId, ncopies)

                # link to file
                # note: mklink requires admin privileges,
                # so must run this script in an admin console
                # eg imageFilepath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                # need to get out of the target dir
                imagePathRelative = '../../../../../../../../' + imageFilepath
                lib.makeSymbolicLinks(targetFolder, imagePathRelative, nfile, ncopies)

                # increment the file number for the target folder
                nfile += ncopies
                nfilesInTargetDir[targetKey] = nfile

        # # check for additional images
        # rowAdditions = lib.getJoinRow(csvAdditions, config.additionsColFileId, fileId)
        # if rowAdditions:
        #     additionId = rowAdditions[config.additionsColAdditionId] # eg C2684338_composite
        #     nframes = int(rowAdditions[config.additionsColNFrames])

        #     # get imagePath

        #     #. how get volume? should the addition col have the whole filepath?
        #     #. and filter?
        #     # eg data/step06_composites/VGISS_7206/C2684338_composite.jpg
        #     # but that ties the data structure down too much
        #     # or else include volume, filter, fileId, but then it's not as general purpose,
        #     # eg for including extraneous images

        #     # one possibility would be to lookup the volume based on the imageId boundaries (fast),
        #     # and then grab whatever image started with the given additionId so don't need filter.
        #     # other extraneous images would have a special prefix, eg 'file:'.

        #     # presumably there wouldn't be a whole lot of these so speed is not too much a factor.

        #     # if '_composite':
        #     #     imageFilepath = lib.getCompositeFilepath(volume, fileId)
        #     # elif '_centered':
        #     #     imageFilepath = lib.getCenteredFilepath(volume, fileId, filter)
        #     # elif '_adjusted':
        #     #     imageFilepath = lib.getAdjustedFilepath(volume, fileId, filter)
        #     # need to insert the additional image here
        #     # add nframes into stage

    fAdditions.close()
    fPositions.close()
    fFiles.close()
    print


# def vgClips(targetPath=None, keepLinks=False):
# def vgClips(volnums=[], imageIds=[], targetPath=None, keepLinks=False):
def vgClips(volnums=None, imageIds=None, targetPath=None, keepLinks=False):
    """
    Build clips associated with the given volumes and target path (eg '//Io').
    """

    # note: targetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(targetPath)

    if keepLinks==False:

        # make sure we have the necessary images
        # if bwOrColor=='bw':
            # lib.loadPreviousStep(targetPathParts, vgCenter.vgCenter)
        # else:
            # lib.loadPreviousStep(targetPathParts, vgComposite.vgComposite)
        lib.loadPreviousStep(targetPathParts, vgComposite.vgComposite)

        # make sure we have some titles
        vgTitles.vgTitles(targetPath)

        # stage images for ffmpeg
        lib.rmdir(config.clipsStageFolder)
        # os.rmdir(config.clipsStageFolder)
        # import shutil
        # shutil.rmtree(config.clipsStageFolder)
        # stageFiles(bwOrColor, targetPathParts)
        # stageFiles(targetPathParts)
        stageFiles(volnums, targetPathParts)

    # build mp4 files from all staged images
    lib.makeVideosFromStagedFiles(config.clipsStageFolder, '../../../../../../',
                                  config.videoFilespec, config.videoFrameRate,
                                  config.clipsMinFrames)


if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # vgClips('bw', 'Jupiter/Voyager1/Io/Narrow')
    # vgClips('bw', '//Triton')
    # vgClips("Neptune")
    # makeLinks()
    makeClipFiles()
    print 'done'


