
# vg center command
# build centered images from adjusted images

import csv
import os
import os.path

import config
import lib
import libimg
import db

import vgAdjust



def vgCenter(volnum, overwrite=False, directCall=True):
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
        if directCall:
            print "Folder exists - skipping vg centers step: " + centersSubfolder
    else:
        # build the adjusted images for the volume, if not already there
        vgAdjust.vgAdjust(volnum, False, False)

        # make new folder
        lib.rmdir(centersSubfolder)
        # lib.mkdir(centersSubfolder)
        os.mkdir(centersSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(adjustmentsSubfolder))

        # read small dbs into memory
        centeringInfo = lib.readCsv(config.centeringdb) # when to turn centering on/off
        targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

        # iterate through all available images, filter on desired volume
        csvFiles, fFiles = lib.openCsvReader(config.filesdb)

        # join on centers.csv file
        csvCenters, fCenters = lib.openCsvReader(config.centersdb)
        csvCenters.next() # skip header row
        fileIdCenters = ''

        # open centers_new.csv file to write any new records to
        csvNewCenters, fNewCenters = lib.openCsvWriter(config.newcentersdb)

        # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
        lastImageInTargetSequence = {}
        
        # # open positions.csv file for target angular size info
        # csvPositions = lib.openCsvReader(config.positionsdb)
        # row2 = csvPositions.next() # skip over fieldnames row
        # fileId2 = ''

        i = 0
        nfile = 1
        volnum = str(volnum) # eg '5101'
        for rowFiles in csvFiles:
            if rowFiles==[] or rowFiles[0][0]=="#": continue # skip blank lines and comments
            if i==0: fields = rowFiles
            else:
                volume = rowFiles[config.filesColVolume]
                if volume!=volnum: continue # filter to given volume

                # get image properties
                fileId = rowFiles[config.filesColFileId]
                filter = rowFiles[config.filesColFilter]
                system = rowFiles[config.filesColPhase]
                craft = rowFiles[config.filesColCraft]
                target = rowFiles[config.filesColTarget]
                camera = rowFiles[config.filesColInstrument]

                # relabel target field if necessary
                target = lib.retarget(targetInfo, fileId, target)

                # get filenames
                infile = lib.getAdjustedFilepath(volume, fileId, filter)
                outfile = lib.getCenteredFilepath(volume, fileId, filter)

                print 'Centering %d/%d: %s     \r' %(nfile,nfiles,infile),
                nfile += 1

                # check if we have the x,y translation for this image file already
                rowCenters, fileIdCenters = lib.getJoinRow(csvCenters, config.centersColFileId,
                                                           fileId, fileIdCenters)
                if rowCenters:
                    x = int(rowCenters[config.centersColX])
                    y = int(rowCenters[config.centersColY])
                    libimg.translateImageFile(infile, outfile, x, y)
                else:
                    targetKey = system + '-' + craft + '-' + target + '-' + camera
                    # do we actually need to center this image?
                    # get centering info from centering.csv
                    centeringInfoRecord = centeringInfo.get(targetKey)
                    if centeringInfoRecord:
                        centeringOff = centeringInfoRecord['centeringOff']
                        centeringOn = centeringInfoRecord['centeringOn']
                        doCenter = (fileId < centeringOff) or (fileId > centeringOn)
                    else: # if no info for this target just center it
                        doCenter = True

                    if target in config.dontCenterTargets: # eg Sky, Dark
                        doCenter = False

                    if doCenter:
                        print
                        print 'currentimage',volume,fileId,filter,targetKey
                        # print lastImageInTargetSequence
                        # x,y = libimg.centerImageFile(infile, outfile)
                        # for this target sequence (eg ariel flyby), what was the last image? 
                        # use that as a fixed image against which we try to align the current image
                        volFileFilter = lastImageInTargetSequence.get(targetKey)
                        if volFileFilter:
                            lastVolume = volFileFilter[0]
                            lastFileId = volFileFilter[1]
                            lastFilter = volFileFilter[2]
                            # lastRadius = volFileFilter[3]
                            fixedfile = lib.getCenteredFilepath(lastVolume, lastFileId, lastFilter)
                            print 'centering against', fixedfile
                        else:
                            fixedfile = None
                        # center the image using blob and hough, then align it to the fixed image
                        x,y,stabilizationOk = libimg.centerAndStabilizeImageFile(infile, outfile, fixedfile)
                        # x,y,stabilizationOk = libimg.centerAndStabilizeImageFile(infile, outfile, fixedfile, lastRadius)
                        print stabilizationOk
                        # if alignment was successful, remember this image
                        if stabilizationOk:
                            lastImageInTargetSequence[targetKey] = [volume, fileId, filter]
                            # lastImageInTargetSequence[targetKey] = [volume, fileId, filter, radius]
                        # else:
                            # stop
                    else:
                        x,y = 399,399

                    print
                    # write x,y to newcenters file
                    rowNew = [volume, fileId, x, y]
                    csvNewCenters.writerow(rowNew)
            i += 1

        fCenters.close()
        fNewCenters.close()
        fFiles.close()

        # now append newcenters records to centers file
        if os.path.isfile(config.newcentersdb):
            lib.concatFiles(config.centersdb, config.newcentersdb)
            lib.rm(config.newcentersdb)
            print
            print 'New records appended to centers.csv file - please make sure the file is sorted before committing it to git'
        else:
            print

                    # mothballing this...
                    # rowPositions, fileIdPositions = lib.getJoinRow(csvPositions,
                    #                                            config.positionsColFileId,
                    #                                            fileId, fileIdPositions)
                    # if rowPositions:
                    #     imageSize = float(rowPositions[config.positionsColImageSize])
                    #     doCenter = (imageSize <= config.centerImageSizeThreshold)
                    # else:
                    #     doCenter = False


if __name__ == '__main__':
    os.chdir('..')
    vgCenter(0)
    print 'done'



