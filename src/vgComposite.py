
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
    # for row in channelRows:
        # print row
    nchannels = len(channelRows)
    print 'Volume %s compositing %d: %s (%d channels)    \r' % \
          (volume,nfile,startId,nchannels),
    if nchannels > 0:
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
            #. may use imageSource to know adjusted vs centered?
            # if don't have a centered file, use the adjusted file
            channelfilepath = lib.getFilepath('center', volume, fileId, filter)
            if not os.path.isfile(channelfilepath):
                channelfilepath = lib.getFilepath('adjust', volume, fileId, filter)
            channel = [filter,channelfilepath,weight,x,y]
            channels.append(channel)

        outfilepath = lib.getFilepath('composite', volume, compositeId)
        im = libimg.combineChannels(channels)
        cv2.imwrite(outfilepath, im)


def vgComposite(filterVolume, filterCompositeId, optionOverwrite=False, directCall=True):
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

    filterVolume = str(filterVolume)
    filterCompositeId = filterCompositeId.upper() # always capital C

    if filterVolume!='':

        inputSubfolder = lib.getSubfolder('center', filterVolume)
        outputSubfolder = lib.getSubfolder('composite', filterVolume)

        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return

        # build the centered images for the volume, if not already there
        vgCenter.vgCenter(filterVolume, '', optionOverwrite=False, directCall=False)

        # make folder
        lib.mkdir(outputSubfolder)

    # read small db into memory
    compositingInfo = lib.readCsv(config.dbCompositing) # when to turn centering on/off

    # should we composite the image?
    compositing = True # default
    compositingMemory = {} # keyed on planet-spacecraft-target-camera

    # iterate over composites.csv records
    csvComposites, fComposites = lib.openCsvReader(config.dbComposites)
    startId = ''
    startVol = ''
    channelRows = []
    nfile = 0
    for row in csvComposites:

        volume = row[config.colCompositesVolume]
        compositeId = row[config.colCompositesCompositeId]

        # filter on volume or composite id
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



