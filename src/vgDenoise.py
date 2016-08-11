
"""
vg denoise command

Attempt to remove different types of noise from images.
"""

import os
import os.path
import cv2

import config
import lib
import libimg
import log

import vgAdjust
# import vgCenter



#. handle indiv imageids
def vgDenoise(volnum='', optionOverwrite=False, directCall=True):
    
    "remove noise from images in given volume"

    volnum = str(volnum) # eg '5101'
    # inputSubfolder = lib.getSubfolder('center', volnum)
    inputSubfolder = lib.getSubfolder('adjust', volnum)
    outputSubfolder = lib.getSubfolder('denoise', volnum)

    if volnum!='':
        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return

        # build the adjusted images for the volume, if not already there
        #. handle indiv images also - could lookup volume by fileid, call vgadjust here
        # vgCenter.vgCenter(volnum, False, False)
        vgAdjust.vgAdjust(volnum, optionOverwrite=False, directCall=False)
        
        # make folder
        lib.mkdir(outputSubfolder)


    # get number of files to process
    nfiles = len(os.listdir(inputSubfolder))

    # read small dbs into memory
    denoisingInfo = lib.readCsv(config.dbDenoising) # when to turn denoising on/off
    
    # iterate through all available images, filter on desired volume or image
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for rowFiles in csvFiles:
        
        volume = rowFiles[config.colFilesVolume]
        fileId = rowFiles[config.colFilesFileId]
        
        # if volume!=volnum and fileId!=buildImageId: continue # filter to given volume/image
        if volume!=volnum: continue # filter to given volume

        # get image properties
        filter = rowFiles[config.colFilesFilter]
        system = rowFiles[config.colFilesSystem]
        craft = rowFiles[config.colFilesCraft]
        target = rowFiles[config.colFilesTarget]
        camera = rowFiles[config.colFilesCamera]
        note = rowFiles[config.colFilesNote]

        # relabel target field if necessary
        # target = lib.retarget(targetInfo, fileId, target)

        # check if we should denoise this image
        doDenoise = True
        denoisingRecord = denoisingInfo.get(fileId)
        if denoisingRecord:
            if denoisingRecord['denoiseImage']=='n': doDenoise = False
        
        if doDenoise:

            # get filenames
            infile = lib.getFilepath('adjust', volume, fileId, filter)
            # infile = lib.getFilepath('center', volume, fileId, filter)
            outfile = lib.getFilepath('denoise', volume, fileId, filter)

            # print 'Volume %s denoising %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
            log.logr('Volume %s denoising %d/%d: %s' % (volume,nfile,nfiles,infile))

            # denoise the image
            #. pass expected target size
            libimg.denoiseImageFile(infile, outfile)

            nfile += 1

    fFiles.close()
    print
    

if __name__ == '__main__':
    os.chdir('..')
    vgDenoise(5101)
    print 'done'

