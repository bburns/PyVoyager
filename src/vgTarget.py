
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

    # iterate down files.csv
    # if target path matches row, copy that image to target subfolder

    volnum = str(volnum)

    # center the volume, if not already there
    vgCenter.vgCenter(volnum, '', False, False)

    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

    # f = open(config.filesdb, 'rt')
    # reader = csv.reader(f)
    reader, f = lib.openCsvReader(config.filesdb)
    for row in reader:
        volume = row[config.filesColVolume]
        if volume==volnum:
            fileId = row[config.filesColFileId]
            filter = row[config.filesColFilter]

            # # get subfolder, eg data/step04_centers/VGISS_5101
            # # sourceFolder = config.centersFolder + 'VGISS_' + volume + '/'

            # # get source filename and path
            # # eg C1327321_RAW_Orange_centered.png
            # # eg data/step04_centers/VGISS_5101/C1327321_RAW_Orange_centered.png
            # # sourceFilename = config.centersPrefix + fileId + '_' + \

            # #. what if targetname ~
            # # C1372372_adjusted_Orange.png
            # # C1372362_centered_Orange.png?
            # # C1372372_composite.png
            # # C1372372_mosaic.png
            # # then would all sort together
            # # sourceFilename = fileId + '_' + config.imageType + '_' + filter + config.centersSuffix + '.png'
            # # sourceFilename = lib.getCenteredFilename(fileId, filter)
            # # sourceFilepath = sourceFolder + sourceFilename
            # sourceFilepath = lib.getCenteredFilepath(fileId, filter)

            # # if centered file doesn't exist, grab the adjusted image instead
            # if not os.path.isfile(sourceFilepath):
            #     # sourceFolder = config.adjustmentsFolder + 'VGISS_' + volume + '/'
            #     # sourceFilename = config.adjustmentsPrefix + fileId + '_' + \
            #     # sourceFilename = fileId + '_' + config.imageType + '_' + filter + config.adjustmentsSuffix + '.png'
            #     # sourceFilename = lib.getAdjustedFilename(fileId, filter)
            #     # sourceFilepath = sourceFolder + sourceFilename
            #     sourceFilepath = lib.getAdjustedFilepath(fileId, filter)

            # get image properties
            phase = row[config.filesColPhase]
            craft = row[config.filesColCraft]
            target = row[config.filesColTarget]
            instrument = row[config.filesColInstrument]

            # relabel target field if necessary - see db/targets.csv for more info
            targetInfoRecord = targetInfo.get(fileId)
            if targetInfoRecord:
                # make sure old target matches what we have
                if targetInfoRecord['oldTarget']==target:
                    target = targetInfoRecord['newTarget']

            # ignore targets like Sky, Dark
            addImage = True
            if target in config.targetsIgnore: addImage = False
            if addImage:

                # create subfolder
                subfolder = phase + '/' + craft + '/' + target +'/' + instrument + '/'
                targetFolder = config.targetsFolder + subfolder
                lib.mkdir_p(targetFolder)

                print 'Volume %s copying %s       \r' % (volume, fileId),

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

