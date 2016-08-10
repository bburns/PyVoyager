
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


# def vgComposite(buildVolnum='', buildCompositeId='', overwrite=False, directCall=True):
# def vgComposite(volnums, imageIds, targetPath, overwrite=False, directCall=True):
def vgComposite(filterVolume, filterImageId, optionOverwrite=False, directCall=True):
    """
    Build composite images by combining channel images.

    Walks over records in composites.csv, merges channel images, writes to composites folder
    eg
        composites.csv:
        volume,compositeId,centerId,filter,weight,x,y
        VGISS_5103,C1537728,C1537728,Blue
        VGISS_5103,C1537728,C1537730,Orange,0.8
        VGISS_5103,C1537728,C1537732,Green,1,10,3
        =>
        step05_composites/VGISS_5103/C1537728_composite.jpg
        Note: weight and x,y are optional - default to 1,0,0
    """

    filterVolume = str(filterVolume)
    filterCompositeId = filterCompositeId.upper() # always capital C

    if filterVolume!='':

        # compositesSubfolder = config.compositesFolder + 'VGISS_' + filterVolume + '/'
        inputSubfolder = lib.getSubfolder('center', filterVolume)
        outputSubfolder = lib.getSubfolder('composite', filterVolume)

        # quit if volume folder exists
        # if os.path.isdir(compositesSubfolder) and optionOverwrite==False:
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Composites folder exists: " + outputSubfolder
            return

        # build the centered images for the volume, if not already there
        vgCenter.vgCenter(filterVolume, '', optionOverwite=False, directCall=False)

        # print 'Building composites for', compositesSubfolder

        # make folder
        # lib.rmdir(compositesSubfolder)
        # lib.mkdir(compositesSubfolder)
        lib.mkdir(outputSubfolder)

    # get centering info - will use to get files from either adjusted or centered folders
    # centeringInfo = lib.readCsv(config.centeringdb)

    # iterate over composites.csv records
    csvComposites, fComposites = lib.openCsvReader(config.compositesdb)
    startId = ''
    startVol = ''
    channelRows = []
    nfile = 0
    for row in csvComposites:

        volume = row[config.compositesColVolume]
        compositeId = row[config.compositesColCompositeId]

        # filter on volume or composite id
        # if volume==filterVolume or compositeId==filterCompositeId:
        if volume!=filterVolume and compositeId!=filterCompositeId: continue

        # gather image filenames into channelRows so can merge them
        if compositeId == startId:
            channelRows.append(row)
        else:
            # we're seeing a new compositeId, so process all the gathered channels
            processChannels(channelRows,startVol,nfile,startId)
            startId = compositeId
            startVol = volume
            channelRows = [row]
            nfile += 1

    # process the last leftover group
    processChannels(channelRows,startVol,nfile,startId)
    print
    fComposites.close()


# def processChannels(channelRows):
def processChannels(channelRows, volume, nfile, startId):
    #. could also have zoom factor, warp info, rotate
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
    Other parameters are just for status update.
    """
    # print channelRows
    nchannels = len(channelRows)
    print 'Volume %s compositing %d: %s (%d channels)    \r' % \
          (volume,nfile,startId,nchannels),
    if nchannels > 0:
        volume = ''
        compositeId = ''
        channels = []
        for row in channelRows:
            compositeId = row[config.compositesColCompositeId]
            fileId = row[config.compositesColFileId]
            volume = row[config.compositesColVolume]
            filter = row[config.compositesColFilter]
            weight = float(row[config.compositesColWeight]) \
                     if len(row)>config.compositesColWeight else 1.0
            x = int(row[config.compositesColX]) if len(row)>config.compositesColX else 0
            y = int(row[config.compositesColY]) if len(row)>config.compositesColY else 0
            #. may use imageSource to know adjusted vs centered?
            # get centered filepath
            # channelfilepath = lib.getCenteredFilepath(volume, fileId, filter)
            channelfilepath = lib.getFilepath('center', volume, fileId, filter)
            # if don't have a centered file, use the adjusted file
            if not os.path.isfile(channelfilepath):
                # channelfilepath = lib.getAdjustedFilepath(volume, fileId, filter)
                channelfilepath = lib.getFilepath('adjust', volume, fileId, filter)
            channel = [filter,channelfilepath,weight,x,y]
            channels.append(channel)

        outfilepath = lib.getCompositeFilepath(volume, compositeId)
        im = libimg.combineChannels(channels)
        cv2.imwrite(outfilepath, im)


if __name__ == '__main__':
    os.chdir('..')
    # buildComposites(5103)
    # buildComposites(8207)
    # vgComposite('','c1617245')

    # ariel - works
    vgComposite('','c2684338',True)
    filename = lib.getCompositeFilepath('7206','c2684338')
    im = cv2.imread(filename)
    libimg.show(im)

    # uranus
    # vgComposite('','C2656801',True)
    # filename = lib.getCompositeFilepath('7205','C2656801')
    # im = cv2.imread(filename)
    # libimg.show(im)

    print 'done'



