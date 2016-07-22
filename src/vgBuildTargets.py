
# vg targets command
# build target subfolders like Jupiter/Voyager1/Io/Narrow
# and copy images to them from a specified volume


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

    targetInfo = lib.readCsv(config.targetsdb) # remapping listed targets

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
                # sourceFolder = config.imagesFolder + 'VGISS_' + volume + '/'
                sourceFolder = config.centersFolder + 'VGISS_' + volume + '/'

                # get source filename and path
                # eg centered_C1327321_RAW_Orange.png
                # eg data/step04_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                # sourceFilename = fileId + '_' + \
                sourceFilename = config.centersPrefix + fileId + '_' + \
                                 config.imageType + '_' + filter + '.png'
                # sourceFilename = fileId + '_' + config.imageType + '_' + filter + '.png'
                sourceFilepath = sourceFolder + sourceFilename

                # if file exists, create subfolder and copy/link image
                # if os.path.isfile(centeredpath):
                if os.path.isfile(sourceFilepath):

                    # get subfolder, eg Jupiter/Voyager1/Io/Narrow
                    phase = row[config.filesColPhase]
                    craft = row[config.filesColCraft]
                    target = row[config.filesColTarget]
                    instrument = row[config.filesColInstrument]
                    subfolder = phase +'/' + craft + '/' + target +'/' + instrument + '/'

                    # translate target
                    # relabel target field if necessary - see db/targets.csv for more info
                    targetInfoRecord = targetInfo.get(fileId)
                    if targetInfoRecord:
                        # make sure old target matches what we have
                        if targetInfoRecord['oldTarget']==target:
                            target = targetInfoRecord['newTarget']

                    # get target file, eg data/step7_targets/jupiter/voyager1/io/narrow/centered_....
                    targetFolder = config.targetsFolder + subfolder
                    targetFilepath = targetFolder + sourceFilename

                    # skip if file already exists (to save time on copying)
                    if True:
                    # if not os.path.isfile(targetFilepath):

                        # create subfolder
                        lib.mkdir_p(targetFolder)

                        # links work, but then can't browse folders with image viewer...
                        # so just copy them

                        # copy file
                        # cp -s, --symbolic-link - make symbolic links instead of copying
                        # [but -s is ignored on windows]
                        # cmd = 'cp ' + centeredpath + ' ' + targetfolder
                        cmd = 'cp ' + sourceFilepath + ' ' + targetFolder
                        print cmd + '      \r',
                        os.system(cmd)

                        # # link to file
                        # # note: mklink requires admin privileges,
                        # # so must run this script in an admin console
                        # # eg ../data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
                        # src2 = '../../../../../' + src # need to get out of the target dir
                        # cmd = 'mklink ' + targetpath + ' ' + src2
                        # cmd = cmd.replace('/','\\')
                        # print cmd
                        # os.system(cmd)

        i += 1

    f.close()
    print


if __name__ == '__main__':
    os.chdir('..')
    buildTargets(8201)
    print 'done'

