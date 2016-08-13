
"""
vg center command

Currently this stabilizes images within a volume - ideally it would distribute
the images to their targets and then stabilize on that sequence, but this works
fairly well, with possible discontinuities at volume boundaries.

Build centers.csv file for a volume by centering and stablizing images in files.csv.
"""

import os
import os.path

import config
import lib
import libimg
import log

import vgDenoise
import vgAdjust


# config.drawCrosshairs = True
# config.drawTarget = True


#. handle target
def vgCenter(filterVolume='', filterImageId='', optionOverwrite=False, directCall=True):
    
    "Build centered and stabilized images for given volume and write x,y,radius to centers.csv"

    filterVolume = str(filterVolume) # eg '5101'
    filterImageId = filterImageId.upper() # always capital C

    #. need to handle indiv imageids - stabilize to the target disc.
    #. will eventually also want to fine tune in relation to previous image.

    # #. if file contains the given volume, either stop or remove those lines
    # s = ',' + filterVolume + ','
    # if lib.fileContainsString(config.dbCenters, s):
    #     if optionOverwrite:
    #         lib.removeLinesFromFile(config.dbCenters, s)
    #     else:
    #         print 'Centers.csv already contains volume ' + filterVolume + ' - run with -y to optionOverwrite'
    #         return

    if filterVolume!='':

        #. just do adjust for now
        # inputSubfolder = lib.getSubfolder('denoise', filterVolume)
        inputSubfolder = lib.getSubfolder('adjust', filterVolume)
        outputSubfolder = lib.getSubfolder('center', filterVolume)

        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return

        # build the previous images for the volume, if not already there
        #. handle indiv images also - could lookup volume by fileid, call vgadjust here
        vgAdjust.vgAdjust(filterVolume, '', optionOverwrite=False, directCall=False)
        # vgDenoise.vgDenoise(filterVolume, optionOverwrite=False, directCall=False)
        
        # create folder
        lib.mkdir(outputSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(inputSubfolder))
    else:
        nfiles = 1

    # read small dbs into memory
    centeringInfo = lib.readCsv(config.dbCentering) # when to turn centering on/off
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # open positions.csv file for target angular size info
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # open centers_new.csv file to write any new records to
    csvNewCenters, fNewCenters = lib.openCsvWriter(config.dbCentersNew)

    # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
    lastImageInTargetSequence = {}

    # iterate through all available images, filter on desired volume or image
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for rowFiles in csvFiles:
        volume = rowFiles[config.colFilesVolume]
        fileId = rowFiles[config.colFilesFileId]
        
        # filter to given volume/image
        if volume!=filterVolume and fileId!=filterImageId: continue 

        # get image properties
        filter = rowFiles[config.colFilesFilter]
        system = rowFiles[config.colFilesSystem]
        craft = rowFiles[config.colFilesCraft]
        target = rowFiles[config.colFilesTarget]
        camera = rowFiles[config.colFilesCamera]
        note = rowFiles[config.colFilesNote]

        # relabel target field if necessary
        target = lib.retarget(retargetingInfo, fileId, target)

        # get filenames
        infile = lib.getFilepath('denoise', volume, fileId, filter)
        if not os.path.isfile(infile): # denoise step is optional - use adjusted file if not there
            infile = lib.getFilepath('adjust', volume, fileId, filter)
        # infile = lib.getFilepath('adjust', volume, fileId, filter)
        outfile = lib.getFilepath('center', volume, fileId, filter)

        # print 'Volume %s centering %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
        log.logr('Volume %s centering %d/%d: %s' % (volume,nfile,nfiles,infile))
        nfile += 1

        # join on positions.csv to get expected target size and radius
        # imageFraction is fraction of image frame taken up by target
        rowPositions = lib.getJoinRow(csvPositions, config.colPositionsFileId, fileId)
        if rowPositions:
            imageFraction = float(rowPositions[config.colPositionsImageFraction])
        else:
            imageFraction = 0 # just rhea and some sky
        targetRadius = int(400*imageFraction) #.param

        # do we actually need to center this image?
        doCenter = lib.centerThisImageQ(imageFraction, centeringInfo, fileId, note, target)
        if doCenter:

            # find center of target using blob and hough, then alignment to fixedimage.
            x,y,foundRadius = libimg.centerImageFile(infile, outfile, targetRadius)
            dx,dy,stabilizationOk = libimg.stabilizeImageFile(outfile, outfile, targetRadius)
            if stabilizationOk:
                x += int(round(dx))
                y += int(round(dy))

            # write x,y,radius to newcenters file
            rowNew = [fileId, volume, x, y, foundRadius]
            csvNewCenters.writerow(rowNew)
            
        else: # don't need to center image, so just copy as is
            
            #. should outfile keep the _denoised or _adjusted tag?
            lib.cp(infile, outfile)
            

    fPositions.close()
    fNewCenters.close()
    fFiles.close()

    # now append newcenters records to centers file
    if os.path.isfile(config.dbCentersNew):
        lib.concatFiles(config.dbCenters, config.dbCentersNew)
        lib.rm(config.dbCentersNew)
        print
        print 'New records appended to centers.csv file - please make sure any ' + \
              'older records are removed and the file is sorted before committing it to git'
    else:
        print


if __name__ == '__main__':
    os.chdir('..')
    vgCenter(5101)
    print 'done'

