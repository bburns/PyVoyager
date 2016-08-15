
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
    Combine channel images into new file.

    channelRows is an array of rows corresponding to rows in the composites.csv file.
    should have [compositeId,centerId,volnum,filter,weight,x,y]
    eg [
      ['C434823','C434823','5101','Orange']
      ['C434823','C434825','5101','Blue','0.8','42','18']
      ['C434823','C434827','5101','Green','1','-50','83']
      ]
    they are combined and written to a file in the composites folder, step05_composites.
    Can have single channel groups.
    If optionAlign is True, will attempt to align the channels,
    and will return updated x,y values.
    """
    #. could also have zoom factor, warp info, rotate
    # for row in channelRows: print row
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
            # if don't have an inpaint or centered file, use the adjusted file
            channelfilepath = lib.getFilepath('inpaint', volume, fileId)
            if os.path.isfile(channelfilepath):
                optionAlign = False # don't try to align already centered images
            else:
                channelfilepath = lib.getFilepath('center', volume, fileId, filter)
            if os.path.isfile(channelfilepath):
                optionAlign = False # don't try to align already centered images
            else:
                channelfilepath = lib.getFilepath('adjust', volume, fileId, filter)
            if os.path.isfile(channelfilepath):
                channel = [filter,channelfilepath,weight,x,y]
                channels.append(channel)

        if len(channels)>0:
            outfilepath = lib.getFilepath('composite', volume, compositeId)
            im, channels = libimg.combineChannels(channels, optionAlign)
            # cv2.imwrite(outfilepath, im)
            # if not cv2.imwrite(outfilepath, im):
            #     outputSubfolder = lib.getSubfolder('composite', volume)
            #     lib.mkdir(outputSubfolder)
            #     cv2.imwrite(outfilepath, im)
            libimg.imwrite(outfilepath, im)
            # print channels
            print [ch[:-1] for ch in channels if ch]


def vgComposite(filterVolume=None, filterCompositeId=None, filterTargetPath=None,
                optionOverwrite=False, optionAlign=False, directCall=True):
    """
    Build composite images by combining channel images.

    Walks over records in composites.csv, merges channel images, writes to composites folder
    eg
        composites.csv:
        compositeId,centerId,volume,filter,weight,x,y
        C1537728,C1537728,5103,Blue
        C1537728,C1537730,5103,Orange,0.8
        C1537728,C1537732,5103,Green,1,10,3
        =>
        step05_composites/VGISS_5103/C1537728_composite.jpg
        Note: weight and x,y are optional - default to 1,0,0
    """

    # filterCompositeId = filterCompositeId.upper() # always capital C
    if filterCompositeId: filterCompositeId = filterCompositeId.upper() # always capital C
    # note: targetPathParts = [system, craft, target, camera]
    targetPathParts = lib.parseTargetPath(filterTargetPath)

    if filterVolume:

        filterVolume = str(filterVolume)
        inputSubfolder = lib.getSubfolder('center', filterVolume)
        # inputSubfolder = lib.getSubfolder('inpaint', filterVolume)
        outputSubfolder = lib.getSubfolder('composite', filterVolume)

        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return

        # build the centered images for the volume, if not already there
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
    if optionAlign: csvNew, fNew = lib.openCsvWriter(config.dbCompositesNew)

    # iterate over composites.csv records
    # csvComposites, fComposites = lib.openCsvReader(config.dbComposites)
    # need access to comments and blank lines so don't use openCsvReader
    fComposites = open(config.dbComposites,'rt')
    csvComposites = csv.reader(fComposites)
    csvComposites.next() # skip header row! #. brittle

    startId = ''
    startVol = ''
    channelRows = []
    nfile = 0
    for row in csvComposites:

        if row==[]: # blank lines
            if optionAlign: csvNew.writerow(row)
            continue
        elif row[0][0]=='#': # comments
            if optionAlign: csvNew.writerow(row)
            continue

        volume = row[config.colCompositesVolume]
        compositeId = row[config.colCompositesCompositeId]
        fileId = row[config.colCompositesFileId]

        # join on files.csv to get more image properties,
        # so can turn compositing on/off with compositing.csv.
        # (need to keep track of which target we're looking at)
        rowFiles = lib.getJoinRow(csvFiles, config.colFilesFileId, compositeId)
        # note: since compositeId repeats, we might have already advanced to the next record,
        # in which case rowFiles will be None. But the target properties will remain the same.
        if rowFiles:
            filter = rowFiles[config.colFilesFilter]
            system = rowFiles[config.colFilesSystem]
            craft = rowFiles[config.colFilesCraft]
            target = rowFiles[config.colFilesTarget]
            camera = rowFiles[config.colFilesCamera]

            # relabel target field if necessary - see db/targets.csv for more info
            target = lib.retarget(retargetingInfo, compositeId, target)

        # filter on volume and composite id and targetpath
        #. test this logic
        volumeOk = (volume==filterVolume if filterVolume else True)
        compositeOk = (compositeId==filterCompositeId if filterCompositeId else True)
        targetPathOk = (lib.targetMatches(targetPathParts, system, craft, target, camera) \
                        if filterTargetPath else True)
        doComposite = volumeOk and compositeOk and targetPathOk

        if doComposite:
            # gather image filenames into channelRows so can merge them
            if compositeId == startId:
                channelRows.append(row)
            else:
                # we're seeing a new compositeId, so process all the gathered channels
                printStatus(channelRows,startVol,nfile,startId)
                processChannels(channelRows,optionAlign)
                startId = compositeId
                startVol = volume
                channelRows = [row]
                nfile += 1

    # process the last leftover group
    printStatus(channelRows,startVol,nfile,startId)
    processChannels(channelRows,optionAlign)

    print
    if optionAlign: fNew.close()
    fFiles.close()
    fComposites.close()


if __name__ == '__main__':
    os.chdir('..')
    # buildComposites(5103)
    # buildComposites(8207)
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
    vgComposite(None,'C1640222',None,optionOverwrite=True, optionAlign=True)
    filename = lib.getFilepath('composite','5117','C1640222')

    im = cv2.imread(filename)
    libimg.show(im)

    # uranus
    # vgComposite(None,'C2656801',True)
    # filename = lib.getFilepath('composite','7205','C2656801')
    # im = cv2.imread(filename)
    # libimg.show(im)

    print 'done'



