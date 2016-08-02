
"""
vg init centers command

Build centers.csv file for a volume by centering and stablizing images in files.csv.

Currently this stabilizes images within a volume - ideally it would distribute
the images to their targets and then stabilize on that sequence, but this works
fairly well, with possible discontinuities at volume boundaries.
"""

import csv
import os
import os.path

import config
import lib
import libimg



def vgInitCenters(volnum):
    "Build centered images for given volume and write x,y,radius to centers.csv"

    volnum = str(volnum)

    #. need to handle indiv imageids? what would stabilization mean then though?
    # stabilize to previous image
    if volnum=='': return

    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + volnum + '/'
    centersSubfolder = config.centersFolder + 'VGISS_' + volnum + '/'

    # make new folder
    lib.rmdir(centersSubfolder)
    os.mkdir(centersSubfolder)

    # get number of files to process
    nfiles = len(os.listdir(adjustmentsSubfolder))

    # read small dbs into memory
    centeringInfo = lib.readCsv(config.centeringdb) # when to turn centering on/off
    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

    # iterate through all available images, filter on desired volume
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)

    # # join on centers.csv file
    # csvCenters, fCenters = lib.openCsvReader(config.centersdb)
    # csvCenters.next() # skip header row #. brittle
    # # fileIdCenters = lib.nextRow(csvCenters, config.centersColFileId)
    # fileIdCenters = ''

    # # join on centersOverride.csv file
    # csvCentersOverride, fCentersOverride = lib.openCsvReader(config.dbCentersOverride)
    # csvCentersOverride.next() # skip header row #. brittle
    # fileIdCentersOverride = ''

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

            # print 'Volume %s centering %d/%d: %s     \r' %(volume,nfile,nfiles,infile),
            print 'Volume %s centering %d/%d: %s' %(volume,nfile,nfiles,infile)
            nfile += 1

            targetKey = system + '-' + craft + '-' + target + '-' + camera

            # do we actually need to center this image?
            doCenter = lib.centerThisImageQ(centeringInfo, targetKey, fileId, target)

            if doCenter==False:
                x,y = 399,399
            else:

                # print
                # print 'currentimage',volume,fileId,filter,targetKey
                # for this target sequence (eg ariel flyby), what was the last good image?
                # use that as a fixed image against which we try to align the
                # current image.
                # we need to remember the fileId, volume, filter, and radius
                lastImageRecord = lastImageInTargetSequence.get(targetKey)
                if lastImageRecord:
                    lastVolume = lastImageRecord[0]
                    lastFileId = lastImageRecord[1]
                    lastFilter = lastImageRecord[2]
                    lastRadius = lastImageRecord[3]
                    fixedfile = lib.getCenteredFilepath(lastVolume, lastFileId, lastFilter)
                    print 'centering against', fixedfile
                else:
                    fixedfile = None
                    lastRadius = 0
                    print 'no image to center against yet for',targetKey

                # #. get x,y = from joined file
                # rowCentersOverride, fileIdCentersOverride = lib.getJoinRow(csvCentersOverride,
                #                                                            config.centersColFileId,
                #                                                            fileId,
                #                                                            fileIdCentersOverride)
                # if rowCentersOverride:
                #     print 'found centers override record - using x,y,radius from that'
                #     x = int(rowCentersOverride[config.centersColX])
                #     y = int(rowCentersOverride[config.centersColY])
                #     radius = int(rowCentersOverride[config.centersColRadius])
                #     # center image at x,y
                #     centerImageFileAt(infile, outfile, x, y)
                # else:
                #     # find center of target
                #     x,y,radius = centerImageFile(infile, outfile)

                # find center of target
                x,y,radius = libimg.centerImageFile(infile, outfile)
                x,y,stabilizationOk = libimg.stabilizeImageFile(infile, outfile, fixedfile,
                                                                lastRadius, x,y,radius)

                # # center the image using blob and hough, then align it to the fixed image
                # # x,y,stabilizationOk = libimg.centerAndStabilizeImageFile(infile, outfile, fixedfile)
                # # x,y,radius,stabilizationOk = libimg.centerAndStabilizeImageFile(infile, outfile, None, lastRadius)
                # # x,y,radius,stabilizationOk = libimg.centerAndStabilizeImageFile(infile, outfile, fixedfile, lastRadius)
                # # if image was successfully stabilized, remember it
                # x,y,radius = centerImageFile(infile, outfile)
                # # given a file to stabilize on, try to stabilize the infile
                # # lastRadius and radius are used to determine if it has changed 'too much'
                # x,y,stabilizationOk = stabilizeImageFile(infile, outfile, fixedfile, lastRadius, x,y,radius)

                if stabilizationOk:
                    lastImageInTargetSequence[targetKey] = [volume, fileId, filter, radius]

                # write x,y,radius to newcenters file
                rowNew = [volume, fileId, x, y, radius]
                #. change to this
                # rowNew = [fileId, volume, x, y, radius]
                csvNewCenters.writerow(rowNew)
        i += 1

    # fCentersOverride.close()
    # fCenters.close()
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
    vgInitCenters(5101)
    print 'done'









# def vgInitCenters(volnum):
#     "Calculate centers for images in the given volume, stabilize and write to db/centers.csv"

#     volnum = str(volnum)

#     # imagespath = lib.getImagespath(volnum)
#     imagesfolder = config.imagesFolder + '/' + imageType + '/VGISS_' + volnum

#     # open the centers<vol>.csv file for writing
#     filename = 'centers' + volumeStr + '.csv'
#     fileout = open(filename, 'wb')
#     fields = 'fileId,x,y'.split(',') # keep in synch with row, below
#     writer = csv.writer(fileout)
#     writer.writerow(fields)

#     # open the files.csv file for reading
#     filein = open(config.filesdb, 'rt')
#     reader = csv.reader(filein)

#     # iterate over all available files
#     i = 0
#     for row in reader:
#         if row==[] or row[0][0]=="#": continue # skip blank line and comments
#         if i==0: fields = row # get column headers
#         else:
#             # get field values
#             # volume,fileid,phase,craft,target,time,instrument,filter,note
#             volume = row[config.filesColVolume] # eg 5101
#             if volume==volumeStr:

#                 fileId = row[config.filesColFileId] # eg C1385455
#                 # phase = row[config.filesColPhase] # eg Jupiter
#                 # craft = row[config.filesColCraft] # eg Voyager1
#                 # target = row[config.filesColTarget] # eg Io
#                 # instrument = row[config.filesColInstrument] # eg Narrow
#                 # filter = row[config.filesColFilter] # eg Orange
#                 # note = row[config.filesColNote]
#                 # print volume, fileId, phase, craft, target, instrument, filter
#                 # if debug: print 'row',row[:-1] # skip note

#                 infiletitle = fileId + '_' + imageType + '_' + filter + '.png'
#                 infilepath = imagesfolder + '/' + infiletitle
#                 print infilepath

#                 center = libimg.findCenter(infilepath)
#                 x,y = center
#                 x = -x
#                 y = -y

#                 row = [fileId,x,y]
#                 print row
#                 writer.writerow(row)

#         i += 1

#     filein.close()
#     fileout.close()

#     #.
#     # blobThreshold = config.blobThreshold
#     # fileid = filename.split('_')[0] # eg C1385455
#     # blobThreshold = getBlobThreshold(fileid)
#     # libimg.centerImageFile(infile, outfile, blobThreshold, config.rotateImage)
#     # libimg.centerImageFile(infile, outfile)


# if __name__ == '__main__':
#     os.chdir('..')
#     vgInitCenters(5101)
#     print 'done'

