"""
vg inpaint command

Fill in gaps in targets, where possible, using pixels from prior frame.
"""

import os
import os.path

import config
import lib
import libimg
import log

# import vgDenoise
# import vgAdjust
import vgCenter


# config.drawCrosshairs = True
# config.drawTarget = True


def vgInpaint(filterVolume='', filterImageId='', optionOverwrite=False, directCall=True):

    filterVolume = str(filterVolume) # eg '5101'
    filterImageId = filterImageId.upper() # always capital C

    if filterVolume!='':

        inputSubfolder = lib.getSubfolder('center', filterVolume)
        outputSubfolder = lib.getSubfolder('inpaint', filterVolume)

        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return

        # build the previous images for the volume, if not already there
        vgCenter.vgCenter(filterVolume, '', optionOverwrite=False, directCall=False)

        # create folder
        lib.mkdir_p(outputSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(inputSubfolder))
    else:
        nfiles = 1

    # read small dbs into memory
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # open positions.csv file for target angular size info
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
    lastImageInTargetSequence = {}

    # iterate through all available images, filter on desired volume or image
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for rowFiles in csvFiles:
        volume = rowFiles[config.colFilesVolume]
        fileId = rowFiles[config.colFilesFileId]

        # filter to given volume/image
        # if volume!=filterVolume and fileId!=filterImageId: continue

        # get image properties
        filter = rowFiles[config.colFilesFilter]
        system = rowFiles[config.colFilesSystem]
        craft = rowFiles[config.colFilesCraft]
        target = rowFiles[config.colFilesTarget]
        camera = rowFiles[config.colFilesCamera]
        # note = rowFiles[config.colFilesNote]

        # relabel target field if necessary
        target = lib.retarget(retargetingInfo, fileId, target)

        # build key
        targetKey = system + '-' + craft + '-' + target + '-' + camera
        # print targetKey

        # get expected angular size (as fraction of frame) and radius
        imageFraction = lib.getImageFraction(csvPositions, fileId)
        targetRadius = int(400*imageFraction) #.param
        # print imageFraction

        # get filenames
        infile = lib.getFilepath('center', volume, fileId, filter)
        outfile = lib.getFilepath('inpaint', volume, fileId)

        # print infile
        # print outfile

        # get previous image, if any
        priorfile = lastImageInTargetSequence.get(targetKey)
        # print priorfile
        if priorfile and imageFraction < 1: #. ?
            if volume==filterVolume or fileId==filterImageId:
                if os.path.isfile(infile):
                    # print infile
                    # print priorfile
                    # print outfile

                    print 'Volume %s inpainting %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
                    nfile += 1

                    # inpaint the image from the prior frame
                    #. might need priorTargetRadius also -
                    # scale priorfile to make them the same size
                    libimg.inpaintImage(infile, priorfile, outfile, targetRadius)

        # remember this image
        lastImageInTargetSequence[targetKey] = infile

    fPositions.close()
    fFiles.close()
    print



if __name__ == '__main__':
    os.chdir('..')
    # vgInpaint(5101)
    # vgInpaint('','C1464114') # first image with gap, in 5101
    vgInpaint('','C1494354')
    print 'done'

