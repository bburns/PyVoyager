
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

    # read small db into memory
    targetInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # iterate down files.csv
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    for row in csvFiles:

        # get image properties
        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]
        filter = row[config.colFilesFilter]
        system = row[config.colFilesSystem]
        craft = row[config.colFilesCraft]
        target = row[config.colFilesTarget]
        camera = row[config.colFilesCamera]

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

            #. at diff times might want diff sources - maybe specify as a cmdline option

            # # copy adjusted file
            # src = lib.getFilepath('adjust', volume, fileId, filter)
            # lib.cp(src, targetFolder)

            # # copy centered file
            # src = lib.getFilepath('center', volume, fileId, filter)
            # lib.cp(src, targetFolder)

            # copy composite file
            src = lib.getFilepath('composite', volume, fileId)
            lib.cp(src, targetFolder)

            # # copy mosaic file
            # src = lib.getFilepath('mosaic', volume, fileId)
            # lib.cp(src, targetFolder)


    fFiles.close()
    print


if __name__ == '__main__':
    os.chdir('..')
    vgTarget(5101)
    print 'done'

