
# vg composite command
# build composite images from centered images,
# based on records in composites.csv.
# see also vgInitComposites.py, which builds initial pass at composites.csv.

import os
import csv
import cv2

import config
import lib
import libimg


import vgCenter


# def buildComposites(volnum, overwrite=False):
def vgComposite(buildVolnum='', buildCompositeId='', overwrite=False):
    "build composite images by combining channel images"

    # walks over records in composites.csv, merges channel images, writes to composites folder
    # eg
    # composites:
    # volume,compositeId,centerId,filter,weight
    # VGISS_5103,C1537728,C1537728,Blue
    # VGISS_5103,C1537728,C1537730,Orange
    # VGISS_5103,C1537728,C1537732,Green

    centersubfolder = config.centersFolder + 'VGISS_' + str(buildVolnum) + '/'
    compositessubfolder = config.compositesFolder + 'VGISS_' + str(buildVolnum) + '/'

    # for test (vol=0), can overwrite test folder
    if os.path.isdir(compositessubfolder) and overwrite==False:
        print "Composites folder exists: " + compositessubfolder
    else:
        # build the centered images for the volume, if not already there
        #. pass imageid also
        vgCenter.vgCenter(buildVolnum, False, False)

        # get centering info - will use to get files from either adjusted or centered folders
        # centeringInfo = lib.readCsv(config.centeringdb)

        # print 'Building composites for', compositessubfolder

        lib.rmdir(compositessubfolder)
        lib.mkdir(compositessubfolder)

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
                # if volnum==vol:
                # print compositeId,buildCompositeId
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
        if len(channelRows)>0:
            print 'Compositing %d: VGISS_%s/%s     \r' % (nfile,startVol,startId),
            processChannels(channelRows)
        print


def processChannels(channelRows):
    "channels is an array of rows corresponding to rows in the composites.csv file"
    # arrays should have [volnum,compositeId,centerId,filter,weight]
    # eg [
    #   [5101,C434823,C434823,Orange]
    #   [5101,C434823,C434825,Blue]
    #   [5101,C434823,C434827,Green]
    #   ]
    # we combine them and write them to a file in the composites folder, step5_composites

    # print channelRows
    channels = {}
    volume = ''
    compositeId = ''
    for row in channelRows:
        volume = 'VGISS_' + row[config.compositesColVolume]
        compositeId = row[config.compositesColCompositeId]
        fileId = row[config.compositesColFileId]
        filter = row[config.compositesColFilter].title()
        # get centered filepath
        # folder = lib.getCenterspath(volume)
        folder = config.centersFolder + volume + '/'
        # filetitle = config.centersPrefix + fileId + '_' + config.imageType + \
        # filetitle = fileId + '_' + config.imageType + '_' + filter + config.centersSuffix + '.png'
        # filetitle = fileId + config.centersSuffix + '_' + filter + config.extension
        filetitle = lib.getCenteredFilename(fileId, filter)
        channelfilepath = folder + filetitle
        # if don't have a centered file, use the adjusted file
        if not os.path.isfile(channelfilepath):
            folder = config.adjustmentsFolder + volume + '/'
            # filetitle = config.adjustmentsPrefix + fileId + '_' + config.imageType + \
            # filetitle = fileId + '_' + config.imageType + '_' + filter + config.adjustmentsSuffix + '.png'
            # filetitle = fileId + '_' + config.adjustmentsSuffix + '_' + filter + config.extension
            filetitle = lib.getAdjustedFilename(fileId, filter)
            channelfilepath = folder + filetitle
        channels[filter] = channelfilepath
    # print channels
    compositesSubfolder = config.compositesFolder + volume + '/'
    # outfilename = compositesSubfolder + config.compositesPrefix + compositeId + '.png'
    # outfilename = compositesSubfolder + compositeId + config.compositesSuffix + '.png'
    outfilename = compositesSubfolder + compositeId + config.compositesSuffix + config.extension
    # print outfilename
    im = libimg.combineChannels(channels)
    cv2.imwrite(outfilename, im)


if __name__ == '__main__':
    os.chdir('..')
    # buildComposites(5103)
    # buildComposites(8207)
    vgComposite('','c1617245')
    print 'done'

