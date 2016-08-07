
"""
vg target command
build target subfolders like Jupiter/Voyager1/Io/Narrow
and copy images to them from a specified volume

symbolic links work, but then can't browse folders with image viewer...
so just copy them
"""

import os
import csv

import config
import lib

import vgCenter



#. handle targetPath
def vgTarget(volnum, targetPath=None):
    "Copy images in given volume to target subfolders"

    volnum = str(volnum)

    # center the volume, if not already there
    vgCenter.vgCenter(volnum, '', False, False)

    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

    # iterate down files.csv
    # if target path matches row, copy that image to target subfolder
    reader, f = lib.openCsvReader(config.filesdb)
    for row in reader:
        volume = row[config.filesColVolume]
        if volume==volnum:
            fileId = row[config.filesColFileId]
            filter = row[config.filesColFilter]

            # get image properties
            phase = row[config.filesColPhase]
            craft = row[config.filesColCraft]
            target = row[config.filesColTarget]
            instrument = row[config.filesColInstrument]

            # relabel target field if necessary - see db/targets.csv for more info
            target = lib.retarget(targetInfo, fileId, target)

            # ignore targets like Sky, Dark
            addImage = True
            if target in config.targetsIgnore: addImage = False
            if addImage:

                # create subfolder
                subfolder = phase + '/' + craft + '/' + target +'/' + instrument + '/'
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

    f.close()
    print


if __name__ == '__main__':
    os.chdir('..')
    vgTarget(8201)
    print 'done'

