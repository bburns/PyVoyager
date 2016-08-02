
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


def vgComposite(buildVolnum='', buildCompositeId='', overwrite=False):
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

    compositesSubfolder = config.compositesFolder + 'VGISS_' + str(buildVolnum) + '/'
    buildCompositeId = buildCompositeId.upper() # always capital C

    if os.path.isdir(compositesSubfolder) and overwrite==False:
        print "Composites folder exists: " + compositesSubfolder
    else:
        # build the centered images for the volume, if not already there
        #. pass imageid also
        if buildVolnum!='':
            vgCenter.vgCenter(buildVolnum, False, False)

        # get centering info - will use to get files from either adjusted or centered folders
        # centeringInfo = lib.readCsv(config.centeringdb)

        # print 'Building composites for', compositesSubfolder

        # if we're building an entire volume, remove the existing directory first
        if buildVolnum!='':
            lib.rmdir(compositesSubfolder)
        lib.mkdir(compositesSubfolder)

        # iterate over composites.csv records
        filein = open(config.compositesdb,'rt')
        reader = csv.reader(filein)
        i = 0
        startId = ''
        startVol = ''
        channelRows = []
        buildVolnum = str(buildVolnum)
        nfile = 0
        for row in reader:
            if row==[] or row[0][0]=="#": continue # skip blank lines and comments
            if i==0: fields = row
            else:
                vol = row[config.compositesColVolume]
                compositeId = row[config.compositesColCompositeId]
                if vol==buildVolnum or compositeId==buildCompositeId:
                    # gather image filenames into channelRows so can merge them
                    # buildComposite(compositeId)
                    if compositeId == startId:
                        channelRows.append(row)
                    else:
                        # we're seeing a new compositeId, so process all the gathered channels
                        if len(channelRows)>0:
                            print 'Volume %s compositing %d: VGISS_%s/%s     \r' \
                                % (vol,nfile,startVol,startId),
                            processChannels(channelRows)
                        startId = compositeId
                        startVol = vol
                        channelRows = [row]
                        nfile += 1
            i += 1
        # do the last leftover group
        if len(channelRows)>0:
            print 'Volume %s compositing %d: VGISS_%s/%s     \r' % \
                  (buildVolnum,nfile,startVol,startId),
            processChannels(channelRows)
        print


def processChannels(channelRows):
    #. could also have zoom factor, warp info, rotate
    """
    Combine channel images into new file.

    channelRows is an array of rows corresponding to rows in the composites.csv file.
    should have [volnum,compositeId,centerId,filter,weight,x,y]
    eg [
      ['5101','C434823','C434823','Orange']
      ['5101','C434823','C434825','Blue','0.8','42','18']
      ['5101','C434823','C434827','Green','1','-50','83']
      ]
    they are combined and written to a file in the composites folder, step05_composites
    """
    # print channelRows
    volume = ''
    compositeId = ''
    channels = []
    for row in channelRows:
        volume = row[config.compositesColVolume]
        compositeId = row[config.compositesColCompositeId]
        fileId = row[config.compositesColFileId]
        filter = row[config.compositesColFilter]
        weight = row[config.compositesColWeight] if len(row)>config.compositesColWeight else 1.0
        x = row[config.compositesColX] if len(row)>config.compositesColX else 0
        y = row[config.compositesColY] if len(row)>config.compositesColY else 0
        #. may use imageSource to know adjusted vs centered
        # get centered filepath
        channelfilepath = lib.getCenteredFilepath(volume, fileId, filter)
        # if don't have a centered file, use the adjusted file
        if not os.path.isfile(channelfilepath):
            channelfilepath = lib.getAdjustedFilepath(volume, fileId, filter)
        channel = [filter,channelfilepath,float(weight),int(x),int(y)]
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
    # vgComposite('','c2684338',True)
    # filename = lib.getCompositeFilepath('7206','c2684338')
    # im = cv2.imread(filename)
    # libimg.show(im)

    # uranus
    vgComposite('','C2656801',True)
    filename = lib.getCompositeFilepath('7205','C2656801')
    im = cv2.imread(filename)
    libimg.show(im)

    print 'done'



