
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



def vgTarget(filterVolume='', filterTargetPath=''):

    "Copy images in given volume to target subfolders"

    filterVolume = str(filterVolume)

    # note: targetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    targetPathParts = lib.parseTargetPath(filterTargetPath)

    # read small db into memory
    targetInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # iterate down files.csv
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
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
        # if filterVolume!='' and volume==filterVolume: addImage = True
        # if targetPathParts and lib.targetMatches(targetPathParts, system, craft, target, camera):
        volumeOk = (filterVolume!='' and volume==filterVolume)
        targetPathOk = lib.targetMatches(targetPathParts, system, craft, target, camera)
        # note AND -
        if volumeOk and targetPathOk:
            addImage = True
        if target in config.targetsIgnore: addImage = False # ignore targets like Sky, Dark
        if addImage:

            # create subfolder
            subfolder = system + '/' + craft + '/' + target +'/' + camera + '/'
            targetFolder = config.folders['target'] + subfolder
            lib.mkdir_p(targetFolder)

            # print 'Volume %s copying %s         \r' % (volume, fileId),
            print 'Volume %s copying %d: %s         \r' % (volume, nfile, fileId),

            #. at diff times might want diff sources - maybe specify as a cmdline option

            src = lib.getFilepath('annotate', volume, fileId)
            if not os.path.isfile(src):
                src = lib.getFilepath('mosaic', volume, fileId)
            if not os.path.isfile(src):
                src = lib.getFilepath('composite', volume, fileId)
            # if not os.path.isfile(src):
                # src = lib.getFilepath('center', volume, fileId, filter)
            # if not os.path.isfile(src):
                # src = lib.getFilepath('denoise', volume, fileId, filter)
            # if not os.path.isfile(src):
                # src = lib.getFilepath('adjust', volume, fileId, filter)
            # if not os.path.isfile(src):
                # src = lib.getFilepath('convert', volume, fileId, filter)

            if os.path.isfile(src):
                lib.cp(src, targetFolder)

            nfile += 1

    fFiles.close()
    print


if __name__ == '__main__':
    os.chdir('..')
    vgTarget(5101)
    print 'done'

