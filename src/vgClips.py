
"""
vg clips command

Build clips associated with target subfolders, eg
> vg clips Jupiter/Voyager1/Io/Narrow

This must be run in an admin console because mklink requires elevated privileges.
"""

import csv
import os
import os.path

import config
import lib

# import vgComposite
import vgAnnotate
import vgTitle



def stageFiles(filterVolumes, filterTargetPath, filterImageIds, stageFolder):
    """
    Make links from source files to clip stage folders.
    This uses mklink which requires admin privileges, so must run in an admin console!
    filterVolumes is a list of volumes as strings, e.g. ['5101','5102'], or None for all.
    filterTargetPath is system/craft/target/camera, e.g. 'Jupiter//Io', or None for all.
    filterImageIds is a string with start and stop imageIds, e.g. 'C1436454-C1528477' or None=all.
    stageFolder is config.clipsStageFolder or config.moviesStageFolder
    This fn is also used by vgMovies, so be careful editing it.
    """
    # targetPathParts is [system, craft, target, camera], or None.
    # ntargetDirFiles is a dictionary that keeps track of how many files each folder contains.

    print 'Making links from source files'

    # print filterVolumes, targetPathParts
    # note: filterTargetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(filterTargetPath)

    if filterImageIds:
        imageIdStart, imageIdStop = filterImageIds.split('-')
    else:
        imageIdStart, imageIdStop = None, None

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
        # ncopies = getNCopies(framerateConstantInfo, target, imageFraction, ncopiesMemory,
        ncopies = lib.getNCopies(framerateConstantInfo, target, imageFraction,
                                 ncopiesMemory, targetKey, framerateInfo, fileId)

        # check if this image matches the volume and target path the user specified on the cmdline
        volumeOk = (volume in filterVolumes if filterVolumes else True)
        targetOk = lib.targetMatches(targetPathParts, system, craft, target, camera)
        imageOk = (fileId >= imageIdStart and fileId <= imageIdStop) if filterImageIds else True
        ignoreTarget = (target in config.clipsIgnoreTargets)
        addImage = volumeOk and targetOk and imageOk and (not ignoreTarget) # <- note ANDs here
        # if targetOk:
        # if fileId=='C1474515':
            # print targetPathParts, system, craft, target, camera
            # print fileId, imageIdStart, imageIdStop
            # print volumeOk, targetOk, imageOk, ignoreTarget, addImage, ncopies
        if addImage:

            if ncopies > 0:

                # use annotated image if available, else mosaic or composite.
                # (don't use centered files or will get bw images mixed in with color).
                imageFilepath = lib.getFilepath('annotate', volume, fileId)
                if not os.path.isfile(imageFilepath):
                    imageFilepath = lib.getFilepath('mosaic', volume, fileId)
                if not os.path.isfile(imageFilepath):
                    imageFilepath = lib.getFilepath('composite', volume, fileId)
                #. added these 2022-05-13 - i guess will need an option for b&w vs color?
                if not os.path.isfile(imageFilepath):
                    imageFilepath = lib.getFilepath('center', volume, fileId, filter)
                if not os.path.isfile(imageFilepath):
                    imageFilepath = lib.getFilepath('adjust', volume, fileId, filter)
                if not os.path.isfile(imageFilepath):
                    imageFilepath = lib.getFilepath('convert', volume, fileId, filter)

                # if image file exists, create subfolder and link image
                if os.path.isfile(imageFilepath):

                    # get staging subfolder and make sure it exists
                    # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/
                    subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                    targetFolder = stageFolder + subfolder
                    lib.mkdir_p(targetFolder)

                    # get current file number in that folder, or start at 0
                    nfile = ntargetDirFiles.get(targetKey) or 0

                    # # if we haven't seen this subfolder before add titlepage a few times.
                    # # titlepages are created in the previous step, vgTitle.
                    # if config.includeTitles and nfile==0:
                    #     titleFilepath = config.folders['titles'] + subfolder + 'title' + \
                    #                          config.extension
                    #     ntitleCopies = config.videoFrameRate * config.titleSecondsToShow
                    #     lib.addImages(titleFilepath, targetFolder, ntitleCopies,
                    #                   ntargetDirFiles, targetKey)

                    print "Volume %s frame: %s x %d           \r" % (volume, fileId, ncopies),

                    # add links to file
                    # note: mklink requires admin privileges, so must run in an admin console
                    # eg imageFilepath=data/step04_centers/VGISS_5101/C1327321_centered.jpg
                    lib.addImages(imageFilepath, targetFolder, ncopies,
                                  ntargetDirFiles, targetKey)

            # check for additional images in additions.csv
            rowAdditions = lib.getJoinRow(csvAdditions, config.colAdditionsFileId, fileId)
            while rowAdditions:
                # additions.csv has fileId,additionId,nframes,tx,ty,scale
                print fileId, rowAdditions
                additionId = rowAdditions[config.colAdditionsAdditionId] # eg C2684338_composite
                ncopies = int(rowAdditions[config.colAdditionsNFrames])
                # tx = int(rowAdditions[config.colAdditionsTx])
                # ty = int(rowAdditions[config.colAdditionsTy])
                # scale = float(rowAdditions[config.colAdditionsScale])
                # tx = int(lib.getCol(rowAdditions, config.colAdditionsTx, 0))
                # ty = int(lib.getCol(rowAdditions, config.colAdditionsTy, 0))
                # scale = int(lib.getCol(rowAdditions, config.colAdditionsScale, 1))

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
                # targetFolder = config.clipsStageFolder + subfolder
                targetFolder = stageFolder + subfolder
                lib.mkdir_p(targetFolder)

                # insert the additional image
                if additionId.startswith('images/'):
                    print 'adding',additionId,targetKey
                    filetitle = additionId[7:] # trim off images/
                    folder = config.folders['additions'] # data/images/
                    imageFilepath = folder + filetitle
                    print imageFilepath
                    # add nframes into stage
                    lib.addImages(imageFilepath, targetFolder, ncopies,
                                  ntargetDirFiles, targetKey)
                else:
                    # handle composite, mosaic, crop, annotate
                    for stage in ['composite','mosaic','crop','annotate']:
                        if additionId.endswith(stage):
                            additionId = additionId.split('_')[0] # remove '_composite', etc
                            #... need to look up correct volume here - might be in different one!
                            imageFilepath = lib.getFilepath(stage, volume, additionId)
                            break
                    print imageFilepath
                    if os.path.isfile(imageFilepath):
                        # add nframes into stage
                        lib.addImages(imageFilepath, targetFolder, ncopies,
                                      ntargetDirFiles, targetKey)
                    else:
                        print "warning: can't find image file",imageFilepath
                rowAdditions = lib.getJoinRow(csvAdditions, config.colAdditionsFileId, fileId)

    fAdditions.close()
    fPositions.close()
    fFiles.close()
    print


def vgClips(filterVolumes=None, filterTargetPath='', keepLinks=False):
    """
    Build clips associated with the given volumes AND target path (eg '//Io').
    """

    #. what does this do? update vg.py help
    if keepLinks==False:

        # make sure we have some titles
        # vgTitle.vgTitle(filterTargetPath)

        # stage images for ffmpeg
        lib.rmdir(config.clipsStageFolder)
        stageFiles(filterVolumes, filterTargetPath, None, config.clipsStageFolder)

    # build mp4 files from all staged images
    lib.makeVideosFromStagedFiles(config.clipsStageFolder, '../../../../../')


if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # vgClips('bw', 'Jupiter/Voyager1/Io/Narrow')
    # vgClips('bw', '//Triton')
    # vgClips("Neptune")
    # makeLinks()
    # makeClipFiles()
    print 'done'


