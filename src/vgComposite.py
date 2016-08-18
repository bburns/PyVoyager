
"""
vg composite command

Build composite images from centered images,
based on records in composites.csv.
See also vgInitComposites.py, which builds initial pass at composites.csv.

Note: even single channel images get a composite image (bw).
Uses centered image if available, otherwise uses the plain adjusted image.
"""

import os
import csv
import cv2

import config
import lib
import libimg


import vgCenter
import vgInpaint


def printStatus(channelRows,volume,nfile,startId):
    "print status message"
    nchannels = len(channelRows)
    print 'Volume %s compositing %d: %s (%d channels)    \r' % \
          (volume,nfile,startId,nchannels),


def processChannels(channelRows, optionAlign):
    """
    Combine channel images into new file, attempting to align them if optionAlign is True.

    channelRows is an array of rows corresponding to rows in the composites.csv file.
    should have [compositeId,centerId,volnum,filter,weight,x,y]
    eg [
      ['C434823','C434823','5101','Orange']
      ['C434823','C434825','5101','Blue','0.8','42','18']
      ['C434823','C434827','5101','Green','1','-50','83']
      ]
    they are combined and written to a file in the composites folder, step05_composites.
    Can have single channel groups.

    If optionAlign is True, will attempt to align the channels, and will return updated
    x,y values in channelRows.
    """
    #. could also have zoom factor, warp info, rotate
    # for row in channelRows: print row
    centered = False
    weightXYFilledOut = False
    if len(channelRows) > 0:
        volume = ''
        compositeId = ''
        channels = []
        for row in channelRows:
            compositeId = row[config.colCompositesCompositeId]
            fileId = row[config.colCompositesFileId]
            volume = row[config.colCompositesVolume]
            filter = row[config.colCompositesFilter]
            weight = float(row[config.colCompositesWeight]) \
                     if len(row)>config.colCompositesWeight else 1.0
            x = int(row[config.colCompositesX]) if len(row)>config.colCompositesX else 0
            y = int(row[config.colCompositesY]) if len(row)>config.colCompositesY else 0

            if len(row)>config.colCompositesWeight: weightXYFilledOut = True

            # if don't have an inpaint or centered file, use the adjusted file
            channelfilepath = lib.getFilepath('inpaint', volume, fileId)
            if os.path.isfile(channelfilepath):
                centered = True
            else:
                channelfilepath = lib.getFilepath('center', volume, fileId, filter)
            if os.path.isfile(channelfilepath):
                centered = True
            else:
                channelfilepath = lib.getFilepath('adjust', volume, fileId, filter)
            if os.path.isfile(channelfilepath):
                channel = [fileId,filter,channelfilepath,weight,x,y]
                channels.append(channel)

        if len(channels)>0:
            outfilepath = lib.getFilepath('composite', volume, compositeId)
            if centered: optionAlign = False # don't try to align images if already centered
            if weightXYFilledOut: optionAlign = False # don't align if already have values

            # combine the channel images
            im, channels = libimg.combineChannels(channels, optionAlign)

            libimg.imwrite(outfilepath, im)
            # if -align: update channels x,y etc
            if optionAlign:
                # make sure all the rows have all their columns
                for row in channelRows:
                    while len(row)<=config.colCompositesY:
                        row.append('')
                # find each row in channelRows and update weights and x,y translation
                for row in channels:
                    for row2 in channelRows:
                        if row2[config.colCompositesFileId]==row[config.colChannelFileId]:
                            row2[config.colCompositesWeight]=row[config.colChannelWeight]
                            row2[config.colCompositesX]=row[config.colChannelX]
                            row2[config.colCompositesY]=row[config.colChannelY]

            # print [ch[:-1] for ch in channels if ch]
        # return channels
    # caller needs to know if x,y values were changed
    xyChanged = not centered
    return xyChanged


def writeUpdates(csvNew, channelRows):
    ""
    for row in channelRows:
        # row = [compositeId, fileId, volume, filter, weight, x, y]
        csvNew.writerow(row)
        # print row



def vgComposite(filterVolume=None, filterCompositeId=None, filterTargetPath=None,
                optionOverwrite=False, optionAlign=False, directCall=True):
    """
    Build composite images by combining channel images.

    Walks over records in composites.csv, merges channel images, writes to composites folder.
    eg
        composites.csv:
        compositeId,centerId,volume,filter,weight,x,y
        C1537728,C1537728,5103,Blue
        C1537728,C1537730,5103,Orange,0.8
        C1537728,C1537732,5103,Green,1,10,3
        =>
        step05_composites/VGISS_5103/C1537728_composite.jpg

    Note: weight,x,y are optional - default to 1,0,0
    """

    if filterCompositeId: filterCompositeId = filterCompositeId.upper() # always capital C

    # note: targetPathParts = [system, craft, target, camera]
    targetPathParts = lib.parseTargetPath(filterTargetPath)

    # build volume for previous step
    if filterVolume:
        filterVolume = str(filterVolume)
        outputSubfolder = lib.getSubfolder('composite', filterVolume)
        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return
        # build the previous step, if not already there
        vgCenter.vgCenter(filterVolume, '', optionOverwrite=False, directCall=False)
        # vgInpaint.vgInpaint(filterVolume, '', optionOverwrite=False, directCall=False)
        # make folder
        lib.mkdir(outputSubfolder)

    # read small dbs into memory
    compositingInfo = lib.readCsv(config.dbCompositing) # when to turn centering on/off
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # open files.csv so can join to it
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)

    # open compositesNew.csv for writing
    if optionAlign:
        lib.rm(config.dbCompositesNew)
        csvNew, fNew = lib.openCsvWriter(config.dbCompositesNew)

    # iterate over composites.csv records
    csvComposites, fComposites = lib.openCsvReader(config.dbComposites)

    startId = ''
    startVol = ''
    channelRows = []
    nfile = 0
    for row in csvComposites:

        # get composite info
        compositeId = row[config.colCompositesCompositeId]
        fileId = row[config.colCompositesFileId]
        volume = row[config.colCompositesVolume]

        # join on files.csv to get more image properties
        # (note: since compositeId repeats, we might have already advanced to the next record,
        # in which case rowFiles will be None. But the target properties will remain the same.)
        rowFiles = lib.getJoinRow(csvFiles, config.colFilesFileId, compositeId)
        if rowFiles:
            # get file info
            filter = rowFiles[config.colFilesFilter]
            system = rowFiles[config.colFilesSystem]
            craft = rowFiles[config.colFilesCraft]
            target = rowFiles[config.colFilesTarget]
            camera = rowFiles[config.colFilesCamera]
            # relabel target field if necessary - see db/targets.csv for more info
            target = lib.retarget(retargetingInfo, compositeId, target)

        # filter on volume, composite id and targetpath
        volumeOk = (volume==filterVolume if filterVolume else True)
        compositeOk = (compositeId==filterCompositeId if filterCompositeId else True)
        targetPathOk = (lib.targetMatches(targetPathParts, system, craft, target, camera) \
                        if filterTargetPath else True)
        doComposite = (volumeOk and compositeOk and targetPathOk)
        if doComposite:
            # gather image filenames into channelRows so can merge them
            if compositeId == startId:
                channelRows.append(row)
            else:
                # we're seeing a new compositeId, so process all the gathered channels
                printStatus(channelRows,startVol,nfile,startId)
                processChannels(channelRows, optionAlign)
                # processChannels(channelRows, optionAlign, csvNew)
                # xyChanged = processChannels(channelRows, optionAlign)
                # if optionAlign and xyChanged:
                    # writeUpdates(csvNew, channelRows)
                startId = compositeId
                startVol = volume
                channelRows = [row]
                nfile += 1

    # process the last leftover group
    print channelRows
    printStatus(channelRows,startVol,nfile,startId)
    processChannels(channelRows, optionAlign)
    # processChannels(channelRows, optionAlign, csvNew)
    # xyChanged = processChannels(channelRows,optionAlign)
    # if optionAlign and xyChanged:
        # writeUpdates(csvNew, channelRows)

    print
    if optionAlign: fNew.close()
    fFiles.close()
    fComposites.close()




if __name__ == '__main__':
    os.chdir('..')

    # vgComposite(5117)
    # vgComposite(8207)
    # vgComposite(None,'c1617245')

    # ariel - works
    # vgComposite(None,'c2684338',None,optionOverwrite=True)
    # automatic - nowork
    # vgComposite(None,'c2684338',None,optionOverwrite=True, optionAlign=True)
    # filename = lib.getFilepath('composite','7206','c2684338')

    # ganymede
    # folder = '../../data/step04_adjust/VGISS_5117/'
    # file1 = folder + 'C1640236_adjusted_Blue.jpg'
    # file2 = folder + 'C1640234_adjusted_Violet.jpg'
    # file3 = folder + 'C1640238_adjusted_Orange.jpg'
    # vgComposite(None,'C1640232',None,optionOverwrite=True, optionAlign=True)
    # filename = lib.getFilepath('composite','5117','C1640232')

    # vgComposite(None,'C1640222',None,optionOverwrite=True, optionAlign=True)
    # filename = lib.getFilepath('composite','5117','C1640222')

    vgComposite(None,'C1642718',None,optionOverwrite=True, optionAlign=True)
    filename = lib.getFilepath('composite','5117','C1642718')
    im = cv2.imread(filename)
    libimg.show(im)

    # uranus
    # vgComposite(None,'C2656801',True)
    # filename = lib.getFilepath('composite','7205','C2656801')
    # im = cv2.imread(filename)
    # libimg.show(im)

    print 'done'



