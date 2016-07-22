
# vg composites command
# build composite images from centered images,
# based on records in composites.csv.
# see also vgInitComposites.py, which builds initial pass at composites.csv.

import os
import csv
import cv2

import config
import lib
import libimg


import vgBuildCenters


def buildComposites(volnum, overwrite=False):
# def buildComposites(volnum='', compositeId='', overwrite=False):
    "build composite images by combining channel images"

    # walks over records in composites.csv, merges channel images, writes to composites folder
    # eg
    # composites:
    # volume,compositeId,centerId,filter,weight
    # VGISS_5103,C1537728,C1537728,Blue
    # VGISS_5103,C1537728,C1537730,Orange
    # VGISS_5103,C1537728,C1537732,Green

    centersubfolder = config.centersFolder + 'VGISS_' + str(volnum) + '/'
    compositessubfolder = config.compositesFolder + 'VGISS_' + str(volnum) + '/'

    # for test (vol=0), can overwrite test folder
    if os.path.isdir(compositessubfolder) and overwrite==False:
        # print "Composites folder exists: " + compositessubfolder
        pass
    else:
        # if volnum!='':

        # build the centered images for the volume, if not already there
        vgBuildCenters.buildCenters(volnum)

        # print 'Building composites for', compositessubfolder

        lib.rmdir(compositessubfolder)
        lib.mkdir(compositessubfolder)

        # iterate over composites.csv records
        filein = open(config.compositesdb,'rt')
        reader = csv.reader(filein)
        i = 0
        startId = ''
        channelRows = []
        volnum = str(volnum)
        nfile = 1
        for row in reader:
            if row==[] or row[0][0]=="#": continue # skip blank lines and comments
            if i==0: fields = row
            else:
                vol = row[config.compositesColVolume]
                compositeId = row[config.compositesColCompositeId]
                if volnum==vol:
                # if volnum==vol or compositeId==:
                    # gather image filenames into channelRows so can merge them
                    # buildComposite(compositeId)
                    if compositeId == startId:
                        channelRows.append(row)
                    else:
                        if len(channelRows)>0:
                            processChannels(channelRows)
                        startId = compositeId
                        channelRows = [row]
                    # print 'compositing %d: %s/%s\r' %(i,volnum,compositeId),
                    # print 'compositing VGISS_%s/%s.png        \r' %(volnum,compositeId),
                    print 'Compositing %d: VGISS_%s/%s.png        \r' %(nfile,volnum,compositeId),
                    nfile += 1
            i += 1
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
        centerId = row[config.compositesColCenterId]
        filter = row[config.compositesColFilter].title()
        # folder = lib.getCenterspath(volume)
        folder = config.centersFolder + volume + '/'
        filetitle = config.centersPrefix + centerId + '_' + config.imageType + '_' + filter + '.png'
        channelfilename = folder + filetitle
        channels[filter] = channelfilename
    compositessubfolder = config.compositesFolder + volume + '/'
    outfilename = compositessubfolder + config.compositesPrefix + compositeId + '.png'
    im = libimg.combineChannels(channels)
    cv2.imwrite(outfilename, im)


if __name__ == '__main__':
    os.chdir('..')
    # buildComposites(5103)
    buildComposites(8207)
    print 'done'

