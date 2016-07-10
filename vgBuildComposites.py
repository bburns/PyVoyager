

import csv
import cv2

import config
import lib
import libimg





def buildComposites(volnum):
    "build composite images by combining channel images"
    # walks over records in composites.txt, merges channel images, writes to composites folder
    # eg
    # composites: 
    # volume,compositeId,centerId,filter,weight
    # VGISS_5103,C1537728,C1537728,Blue
    # VGISS_5103,C1537728,C1537730,Orange
    # VGISS_5103,C1537728,C1537732,Green
    # files:
    # VGISS_5103,C1537728,Jupiter,Voyager1,Jupiter,Narrow,BLUE,3 COLOR ROTATION MOVIE
    # VGISS_5103,C1537730,Jupiter,Voyager1,Jupiter,Narrow,ORANGE,3 COLOR ROTATION MOVIE
    # VGISS_5103,C1537732,Jupiter,Voyager1,Jupiter,Narrow,GREEN,3 COLOR ROTATION MOVIE
    
    # iterate over composites.txt records
    filein = open(config.compositesdb,'rt')
    reader = csv.reader(filein)
    i = 0
    startId = ''
    channelRows = []
    volume = lib.getVolumeTitle(volnum)
    for row in reader:
        if i==0:
            fields = row
        else:
            vol = row[0]
            if volume==vol:
                compositeId = row[1]
                if compositeId == startId:
                    channelRows.append(row)
                else:
                    if len(channelRows)>0:
                        processChannels(channelRows)
                    startId = compositeId
                    channelRows = [row]
        i += 1
    processChannels(channelRows)
            
    
def processChannels(channelRows):
    "channels is an array of rows corresponding to rows in the composites.txt file"
    # volnum,compositeId,centerId,filter,weight
    channels = {}
    volume = ''
    compositeId = ''
    for row in channelRows:
        volume = row[0]
        compositeId = row[1]
        centerId = row[2]
        filter = row[3].title()
        # folder = lib.getCenterspath(volume)
        folder = config.centersFolder + '/' + volume
        filetitle = config.centersprefix + centerId + '_' + config.imageType + '_' + filter + '.png'
        channelfilename = folder + '/' + filetitle
        channels[filter] = channelfilename
    print channels
    folder = config.compositesFolder + '/' + volume
    lib.mkdir(folder)
    outfilename = folder + '/' + config.compositesPrefix + compositeId + '.png'
    print outfilename
    im = libimg.combineChannels(channels)
    cv2.imwrite(outfilename, im)
    

if __name__ == '__main__':
    buildComposites(5103)
    print 'done'
