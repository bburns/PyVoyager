
"""
vg map command

Build up 2d color maps of targets
"""

import os
import os.path

import numpy as np
import cv2
import math



import config
import lib
import libimg
import log


#. handle targetpath
def vgMap(filterVolume='', optionOverwrite=False, directCall=True):
# def vgMap(filterVolume='', filterTargetPath='', optionOverwrite=False, directCall=True):
    
    "Build up 2d color map"

    if filterVolume:
        filterVolume = str(filterVolume)
        
    outputSubfolder = lib.getSubfolder('map', filterVolume)

    # create folder
    lib.mkdir(outputSubfolder)


    # # read small dbs into memory
    # centeringInfo = lib.readCsv(config.dbCentering) # when to turn centering on/off
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # open positions.csv file for target angular size info
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # # open centers_new.csv file to write any new records to
    # csvNewCenters, fNewCenters = lib.openCsvWriter(config.dbCentersNew)

    # # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
    # lastImageInTargetSequence = {}
    
    
    # set up blank mapping fn h(x,y) = (hx(x,y), hy(x,y))
    hx = np.zeros((800,1600),np.float32)
    hy = np.zeros((800,1600),np.float32)


    # iterate through all available images, filter on desired volume or image
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for rowFiles in csvFiles:
        volume = rowFiles[config.colFilesVolume]
        fileId = rowFiles[config.colFilesFileId]
        
        # filter to given volume
        if volume!=filterVolume: continue 

        # get image properties
        filter = rowFiles[config.colFilesFilter]
        system = rowFiles[config.colFilesSystem]
        craft = rowFiles[config.colFilesCraft]
        target = rowFiles[config.colFilesTarget]
        camera = rowFiles[config.colFilesCamera]
        note = rowFiles[config.colFilesNote]

        # relabel target field if necessary
        target = lib.retarget(retargetingInfo, fileId, target)

        #. skip others
        if target!='Jupiter': continue
        if fileId < 'C1462331': continue
        
        # get filenames
        infile = lib.getFilepath('composite', volume, fileId)
        if not os.path.isfile(infile):
            print 'warning file not found', infile
            continue

        print 'Volume %s mapping %d: %s      \r' % (volume,nfile,infile),
        nfile += 1

        # get expected angular size (as fraction of frame) and radius
        imageFraction = lib.getImageFraction(csvPositions, fileId)
        targetRadius = int(400*imageFraction) #.param

        r = targetRadius
        
        im = cv2.imread(infile)
        libimg.show(im)

        # mx,my = map x,y on scale 0 to 1600, 0 to 800
        for mx in xrange(800): # 0 to pi = front half of sphere
            for my in xrange(800):
                
                # qx,qy = map x,y on scale 0 to 2pi, -1 to 1
                qx = mx * 2 * math.pi / 1600
                qy = -(my-400)/400
                
                # px,py = image x,y on scale -1 to 1, -1 to 1, with 1=targetradius
                if abs(qy)<1:
                    px = -math.sqrt(1 - qy**2) + math.cos(qx)
                else:
                    px = 0
                py = qy
                
                # sx,sy = image x,y on scale 0 to 800, 0 to 800
                sx = px * r + 400
                sy = -py * r + 400
                
                hx[my][mx] = sx
                hy[my][mx] = sy
                
        map = cv2.remap(im, hx, hy, cv2.INTER_LINEAR)
        
        libimg.show(map)

        #. now need to blend this into the main map
        
        
        
        

    fPositions.close()
    fFiles.close()

    print
    

if __name__ == '__main__':
    os.chdir('..')
    vgMap(5101)
    print 'done'

