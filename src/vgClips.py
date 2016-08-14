
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

# import vgComposite
import vgAnnotate
import vgTitles



def getNCopies(framerateConstantInfo, target, imageFraction, ncopiesMemory, targetKey,
               framerateInfo, fileId):
    """
    How many copies of the given target do we need?
    Bases it on imageFraction, information in targets.csv, framerates.csv, etc.
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


def addImages(imageFilepath, targetFolder, ncopies, ntargetDirFiles, targetKey):
    """
    add symbolic links from imageFilepath to target folder and update nfile count for target.
    """
    nfile = ntargetDirFiles.get(targetKey) or 0
    # need to get out of the target dir - we're always this deep - could parameterize if needed
    imagePathRelative = '../../../../../../../' + imageFilepath
    lib.makeSymbolicLinks(imagePathRelative, targetFolder, nfile, ncopies)
    # increment the file number for the target folder
    nfile += ncopies
    ntargetDirFiles[targetKey] = nfile


def stageFiles(filterVolumes, targetPathParts):
    """
    Make links from source files to clip stage folders.
    filterVolumes is a list of volumes as strings, e.g. ['5101','5102']
    targetPathParts is [system, craft, target, camera]
    """

    print 'Making links from source files'

    # print filterVolumes, targetPathParts

    # read some small dbs into memory
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets
    framerateConstantInfo = lib.readCsv(config.dbFramerateConstants) # change framerate per target
    framerateInfo = lib.readCsv(config.dbFramerates) # change framerate per image
    centeringInfo = lib.readCsv(config.dbCentering) # turn centering on/off

    # keep track of number of files in each target subfolder,
    # so we can number files appropriately and know when to add titles
    ntargetDirFiles = {}

    # how many times should we duplicate the images?
    ncopies = 1 # default
    ncopiesMemory = {} # keyed on planet-spacecraft-target-camera

    # open positions.csv file for target angular size info (used to control effective framerate)
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # open additions.csv for additional images to insert into sequence
    csvAdditions, fAdditions = lib.openCsvReader(config.dbAdditions)

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    for row in csvFiles:

        # get file info
        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]
        filter = row[config.colFilesFilter]
        system = row[config.colFilesSystem]
        craft = row[config.colFilesCraft]
        target = row[config.colFilesTarget]
        camera = row[config.colFilesCamera]

        # relabel target field if necessary - see db/targets.csv for more info
        target = lib.retarget(retargetingInfo, fileId, target)

        # get expected angular size (as fraction of frame)
        imageFraction = lib.getImageFraction(csvPositions, fileId)

        # build a key
        targetKey = system + '-' + craft + '-' + target + '-' + camera

        # how many copies of this image do we want?
        # note: we need to do this even if we don't add this image,
        # because need to keep track of sticky overrides from framerates.csv.
        ncopies = getNCopies(framerateConstantInfo, target, imageFraction, ncopiesMemory,
                             targetKey, framerateInfo, fileId)

        # does this image match the volume and target path the user specified on the cmdline?
        addImage = False
        # note AND -
        if (volume in filterVolumes) and \
           lib.targetMatches(targetPathParts, system, craft, target, camera):
            addImage = True
        if target in config.clipsIgnoreTargets: addImage = False
        # if addImage and ncopies > 0:
        if addImage:

            if ncopies > 0:
                # use annotated image if available, else mosaic or composite.
                # but don't use centered files or will get bw images mixed in with color.
                imageFilepath = lib.getFilepath('annotate', volume, fileId)
                if not os.path.isfile(imageFilepath):
                    imageFilepath = lib.getFilepath('mosaic', volume, fileId)
                if not os.path.isfile(imageFilepath):
                    imageFilepath = lib.getFilepath('composite', volume, fileId)

                # if image file exists, create subfolder and link image
                if os.path.isfile(imageFilepath):

                    # get staging subfolder and make sure it exists
                    # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/
                    subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                    targetFolder = config.clipsStageFolder + subfolder
                    lib.mkdir_p(targetFolder)

                    # get current file number in that folder, or start at 0
                    nfile = ntargetDirFiles.get(targetKey) or 0

                    # if we haven't seen this subfolder before add titlepage a few times.
                    # titlepages are created in the previous step, vgTitle.
                    if config.includeTitles and nfile==0:
                        titleFilepath = config.folders['titles'] + subfolder + 'title' + \
                                             config.extension
                        ntitleCopies = config.videoFrameRate * config.titleSecondsToShow
                        addImages(titleFilepath, targetFolder, ntitleCopies,
                                  ntargetDirFiles, targetKey)

                    print "Volume %s frame: %s x %d           \r" % (volume, fileId, ncopies),

                    # add links to file
                    # note: mklink requires admin privileges, so must run in an admin console
                    # eg imageFilepath=data/step04_centers/VGISS_5101/C1327321_centered.jpg
                    addImages(imageFilepath, targetFolder, ncopies, ntargetDirFiles, targetKey)

            # check for additional images in additions.csv
            rowAdditions = lib.getJoinRow(csvAdditions, config.colAdditionsFileId, fileId)
            if rowAdditions:
                print fileId, rowAdditions
                additionId = rowAdditions[config.colAdditionsAdditionId] # eg C2684338_composite
                ncopies = int(rowAdditions[config.colAdditionsNFrames])

                # get imagePath
                #. how get volume from fileId like C2684338?
                # eg data/step06_composites/VGISS_7206/C2684338_composite.jpg
                # get folder step06 from suffix, _composite.
                # could lookup the volume based on the imageId boundaries, and then grab
                # whatever image started with the given additionId so don't need filter.
                # other extraneous images would have a special prefix, eg 'images/'.

                # get staging subfolder and make sure it exists
                # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/
                subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                targetFolder = config.clipsStageFolder + subfolder
                lib.mkdir_p(targetFolder)

                if additionId.startswith('images/'):
                    print 'adding',additionId,targetKey
                    filetitle = additionId[7:] # trim off images/
                    folder = config.folders['additions'] # data/images/
                    imageFilepath = folder + filetitle
                    print imageFilepath
                    addImages(imageFilepath, targetFolder, ncopies, ntargetDirFiles, targetKey)
                else:
                    print 'unhandled addition', additionId
                    # if '_composite':
                    #     imageFilepath = lib.getCompositeFilepath(volume, fileId)
                    # elif '_centered':
                    #     imageFilepath = lib.getCenteredFilepath(volume, fileId, filter)
                    # elif '_adjusted':
                    #     imageFilepath = lib.getAdjustedFilepath(volume, fileId, filter)
                    # need to insert the additional image here
                    # add nframes into stage

    fAdditions.close()
    fPositions.close()
    fFiles.close()
    print


def vgClips(filterVolumes=None, filterTargetPath='', keepLinks=False):
    """
    Build clips associated with the given volumes AND target path (eg '//Io').
    """

    # note: filterTargetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(filterTargetPath)

    if keepLinks==False:

        # make sure we have the necessary images
        # if bwOrColor=='bw':
            # lib.loadPreviousStep(targetPathParts, vgCenter.vgCenter)
        # else:
            # lib.loadPreviousStep(targetPathParts, vgComposite.vgComposite)
        # lib.loadPreviousStep(targetPathParts, vgComposite.vgComposite)
        #. fix
        # lib.loadPreviousStep(targetPathParts, vgAnnotate.vgAnnotate)

        # make sure we have some titles
        vgTitles.vgTitles(filterTargetPath)

        # stage images for ffmpeg
        lib.rmdir(config.clipsStageFolder)
        stageFiles(filterVolumes, targetPathParts)

    # build mp4 files from all staged images
    lib.makeVideosFromStagedFiles(config.clipsStageFolder, '../../../../../',
                                  config.videoFilespec, config.videoFrameRate,
                                  config.clipsMinFrames)


if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # vgClips('bw', 'Jupiter/Voyager1/Io/Narrow')
    # vgClips('bw', '//Triton')
    # vgClips("Neptune")
    # makeLinks()
    # makeClipFiles()
    print 'done'


