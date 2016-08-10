
"""
vg target command

Build target subfolders like Jupiter/Voyager1/Io/Narrow,
and copy images to them from a specified volume.

Symbolic links work, but then can't browse folders with image viewer...
so just copy them.
"""

import os
import csv

import config
import lib

import vgCenter



#. handle targetPath
def vgTarget(filterVolume='', targetPath=''):
    "Copy images in given volume to target subfolders"

    filterVolume = str(filterVolume)

    # note: targetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(targetPath)

    # center the volume, if not already there
    vgCenter.vgCenter(filterVolume, '', False, False)

    # read small db into memory
    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

    # iterate down files.csv
    # if target path matches row, copy that image to target subfolder
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)
    for row in csvFiles:

        # get image properties
        volume = row[config.filesColVolume]
        fileId = row[config.filesColFileId]
        filter = row[config.filesColFilter]
        system = row[config.filesColPhase]
        craft = row[config.filesColCraft]
        target = row[config.filesColTarget]
        camera = row[config.filesColInstrument]

        # relabel target field if necessary - see db/targets.csv for more info
        target = lib.retarget(targetInfo, fileId, target)

        # should we add this image?
        addImage = False
        if filterVolume!='' and volume==filterVolume: addImage = True
        if targetPathParts and lib.targetMatches(targetPathParts, system, craft, target, camera):
            addImage = True
        if target in config.targetsIgnore: addImage = False # ignore targets like Sky, Dark
        if addImage:

            # create subfolder
            subfolder = system + '/' + craft + '/' + target +'/' + camera + '/'
            targetFolder = config.targetsFolder + subfolder
            lib.mkdir_p(targetFolder)

            print 'Volume %s copying %s         \r' % (volume, fileId),

            # copy adjusted file
            src = lib.getAdjustedFilepath(volume, fileId, filter)
            lib.cp(src, targetFolder)

            # copy centered file
            src = lib.getCenteredFilepath(volume, fileId, filter)
            lib.cp(src, targetFolder)

            # copy composite file
            src = lib.getCompositeFilepath(volume, fileId)
            lib.cp(src, targetFolder)

            # # copy mosaic file
            # src = lib.getMosaicFilepath(fileId, filter)
            # shutil.copy(src, targetFolder)

    fFiles.close()
    print


if __name__ == '__main__':
    os.chdir('..')
    vgTarget(5101)
    print 'done'

