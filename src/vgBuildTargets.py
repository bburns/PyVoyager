
# vg targets command
# build target subfolders like Jupiter/Voyager1/Io/Narrow
# and copy images to them from a specified volume

# links work, but then can't browse folders with image viewer...
# so just copy them


import os
import csv

import config
import lib

import vgBuildCenters


#. handle targetPath
def buildTargets(volnum, targetPath=None):
    "Copy images in given volume to target subfolders"

    # iterate down files.csv
    # if target path matches row, copy that image to target subfolder

    volnum = str(volnum)

    # center the volume, if not already there
    vgBuildCenters.buildCenters(volnum)

    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

    f = open(config.filesdb, 'rt')
    i = 0
    reader = csv.reader(f)
    for row in reader:
        if row==[] or row[0][0]=="#": continue # ignore blank lines and comments
        if i==0: fields = row
        else:
            volume = row[config.filesColVolume]
            if volume==volnum:
                fileId = row[config.filesColFileId]
                filter = row[config.filesColFilter]

                # get subfolder, eg data/step04_centers/VGISS_5101
                sourceFolder = config.centersFolder + 'VGISS_' + volume + '/'

                # get source filename and path
                # eg C1327321_RAW_Orange_centered.png
                # eg data/step04_centers/VGISS_5101/C1327321_RAW_Orange_centered.png
                # sourceFilename = config.centersPrefix + fileId + '_' + \
                sourceFilename = fileId + '_' + config.imageType + '_' + filter + \
                                 config.centersSuffix + '.png'
                sourceFilepath = sourceFolder + sourceFilename

                # if centered file doesn't exist, grab the adjusted image instead
                if not os.path.isfile(sourceFilepath):
                    sourceFolder = config.adjustmentsFolder + 'VGISS_' + volume + '/'
                    # sourceFilename = config.adjustmentsPrefix + fileId + '_' + \
                    sourceFilename = fileId + '_' + config.imageType + '_' + filter + \
                                     config.adjustmentsSuffix + '.png'
                    sourceFilepath = sourceFolder + sourceFilename

                targetFilename = sourceFilename

                # create subfolder and copy/link image

                # translate target
                # relabel target field if necessary - see db/targets.csv for more info
                targetInfoRecord = targetInfo.get(fileId)
                if targetInfoRecord:
                    # make sure old target matches what we have
                    if targetInfoRecord['oldTarget']==target:
                        target = targetInfoRecord['newTarget']

                # get subfolder, eg Jupiter/Voyager1/Io/Narrow
                phase = row[config.filesColPhase]
                craft = row[config.filesColCraft]
                target = row[config.filesColTarget]
                instrument = row[config.filesColInstrument]
                subfolder = phase +'/' + craft + '/' + target +'/' + instrument + '/'

                # ignore targets like Sky, Dark
                addImage = True
                if target in config.targetsIgnore: addImage = False
                if addImage:

                    # get target file,
                    # eg data/step07_targets/jupiter/voyager1/io/narrow/centered_....
                    targetFolder = config.targetsFolder + subfolder
                    targetFilepath = targetFolder + targetFilename

                    # create subfolder
                    lib.mkdir_p(targetFolder)

                    # copy file
                    # cp -s, --symbolic-link - make symbolic links instead of copying
                    # [but -s is ignored on windows]
                    # cmd = 'cp ' + centeredpath + ' ' + targetfolder
                    # cmd = 'cp ' + sourceFilepath + ' ' + targetFolder
                    cmd = 'cp ' + sourceFilepath + ' ' + targetFilepath
                    print cmd + '      \r',
                    os.system(cmd)

        i += 1

    f.close()
    print


if __name__ == '__main__':
    os.chdir('..')
    buildTargets(8201)
    print 'done'

