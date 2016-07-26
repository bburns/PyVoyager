
# vg centers command
# build centered images from adjusted images

import csv
import os
import os.path

import config
import lib
import libimg
import db

import vgBuildAdjustments


def buildCenters(volnum, overwrite=False):
    "Build centered images for given volume, if they don't exist yet"

    #. need to handle indiv imageids
    if volnum=='': return

    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + str(volnum) + '/'
    centersSubfolder = config.centersFolder + 'VGISS_' + str(volnum) + '/'

    if int(volnum)==0: # test volume - turn on image debugging
        config.drawBoundingBox = True
        config.drawCircle = True
        config.drawCrosshairs = True

    # for test (vol=0), can overwrite test folder
    if int(volnum)!=0 and os.path.isdir(centersSubfolder) and overwrite==False:
        # print "Folder exists - skipping vg centers step: " + centersSubfolder
        pass
    else:
        # build the adjusted images for the volume, if not already there
        vgBuildAdjustments.buildAdjustments(volnum)

        # make new folder
        lib.rmdir(centersSubfolder)
        lib.mkdir(centersSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(adjustmentsSubfolder))

        # read small dbs into memory
        centeringInfo = lib.readCsv(config.centeringdb) # when to turn centering on/off
        targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

        # iterate through all available images, filter on desired volume
        f = open(config.filesdb, 'rt')
        reader = csv.reader(f)

        # # open positions.csv file for target angular size info
        # f2 = open(config.positionsdb, 'rt')
        # reader2 = csv.reader(f2)
        # row2 = reader2.next() # skip over fieldnames row
        # fileId2 = ''

        i = 0
        nfile = 1
        volnum = str(volnum) # eg '5101'
        for row in reader:
            if row==[] or row[0][0]=="#": continue # skip blank lines and comments
            if i==0: fields = row
            else:
                volume = row[config.filesColVolume]
                if volume==volnum:
                    fileId = row[config.filesColFileId]
                    filter = row[config.filesColFilter]
                    system = row[config.filesColPhase]
                    craft = row[config.filesColCraft]
                    target = row[config.filesColTarget]
                    camera = row[config.filesColInstrument]

                    # relabel target field if necessary - see db/targets.csv for more info
                    #. make lib fn
                    targetInfoRecord = targetInfo.get(fileId)
                    if targetInfoRecord:
                        # make sure old target matches what we have
                        if targetInfoRecord['oldTarget']==target:
                            target = targetInfoRecord['newTarget']

                    # skip this image if don't want target centered (eg Sky, Dark)
                    if target in config.dontCenterTargets:
                        continue

                    # mothballing this...
                    # # skip ahead in positions.csv until reach same record (if there)
                    # while fileId2 < fileId:
                    #     try:
                    #         row2 = reader2.next()
                    #     except:
                    #         break # if reached eof just stop
                    #     fileId2 = row2[config.positionsColFileId]
                    # # if the same record is there, check if we need to center image
                    # if fileId2 == fileId:
                    #     imageSize = float(row2[config.positionsColImageSize])
                    #     doCenter = (imageSize <= config.centerImageSizeThreshold)
                    # else:
                    #     # otherwise don't center it
                    #     doCenter = False
                    # print fileId, row2, doCenter

                    # get the centering info, if any
                    # info includes planetCraftTargetCamera,centeringOff,centeringOn
                    # planetCraftTargetCamera = system + craft + target + camera
                    planetCraftTargetCamera = system + '-' + craft + '-' + target + '-' + camera
                    centeringInfoRecord = centeringInfo.get(planetCraftTargetCamera)
                    if centeringInfoRecord:
                        centeringOff = centeringInfoRecord['centeringOff']
                        centeringOn = centeringInfoRecord['centeringOn']
                        doCenter = (fileId < centeringOff) or (fileId > centeringOn)
                    else: # if no info for this target just center it
                        doCenter = True

                    if doCenter:
                        # center the file
                        # adjustedFilename = config.adjustmentsPrefix + fileId + '_' + \
                        # adjustedFilename = fileId + '_' + config.imageType + '_' + filter + config.adjustmentsSuffix + '.png'
                        # adjustedFilename = fileId + config.adjustmentsSuffix + '_' + filter + config.extension
                        adjustedFilename = lib.getAdjustedFilename(fileId, filter)
                        infile = adjustmentsSubfolder + adjustedFilename
                        # centeredFilename = config.centersPrefix + adjustedFilename[9:] # remove 'adjusted_'
                        # centeredFilename = fileId + '_' + config.imageType + '_' + filter + config.centersSuffix + '.png'
                        # centeredFilename = fileId + config.centersSuffix + '_' + filter + config.extension
                        centeredFilename = lib.getCenteredFilename(fileId, filter)
                        outfile = centersSubfolder + centeredFilename
                        # print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                        # print 'Centering %d: %s     \r' %(nfile,infile),
                        print 'Centering %d/%d: %s     \r' %(nfile,nfiles,infile),
                        if os.path.isfile(infile):
                            libimg.centerImageFile(infile, outfile)
                        else:
                            print 'Warning: missing image file', infile

                    nfile += 1

            i += 1

        f.close()
        # f2.close()

        print

if __name__ == '__main__':
    os.chdir('..')
    buildCenters(0)
    print 'done'



