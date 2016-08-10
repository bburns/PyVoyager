
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



def vgDenoise(buildVolnum='', buildImageId='', overwrite=False, directCall=True):
    "remove noise from images"

    buildVolnum = str(buildVolnum) # eg '5101'
    buildImageId = buildImageId.upper() # always capital C

    #. handle indiv imageids

    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + buildVolnum + '/'
    denoisedSubfolder = config.denoisedFolder + 'VGISS_' + buildVolnum + '/'

    if buildVolnum!='':
        if os.path.isdir(denoisedSubfolder) and overwrite==False:
            if directCall:
                print "Folder exists - skipping vg denoise step: " + denoisedSubfolder
            return

        # build the adjusted images for the volume, if not already there
        #. handle indiv images also - could lookup volume by fileid, call vgadjust here
        vgAdjust.vgAdjust(buildVolnum, False, False)
        
        # if we're building an entire volume, remove the existing directory first
        lib.rmdir(denoisedSubfolder)
        os.mkdir(denoisedSubfolder)


    # get number of files to process
    nfiles = len(os.listdir(adjustmentsSubfolder))

    # iterate through all available images, filter on desired volume or image
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)
    nfile = 1
    for rowFiles in csvFiles:
        
        volume = rowFiles[config.filesColVolume]
        fileId = rowFiles[config.filesColFileId]
        
        if volume!=buildVolnum and fileId!=buildImageId: continue # filter to given volume/image

        # get image properties
        filter = rowFiles[config.filesColFilter]
        system = rowFiles[config.filesColPhase]
        craft = rowFiles[config.filesColCraft]
        target = rowFiles[config.filesColTarget]
        camera = rowFiles[config.filesColInstrument]
        note = rowFiles[config.filesColNote]

        # relabel target field if necessary
        # target = lib.retarget(targetInfo, fileId, target)

        # get filenames
        infile = lib.getAdjustedFilepath(volume, fileId, filter)
        outfile = lib.getDenoisedFilepath(volume, fileId, filter)

        # print 'Volume %s denoising %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
        log.logr('Volume %s denoising %d/%d: %s' % (volume,nfile,nfiles,infile))
        
        libimg.denoiseImageFile(infile, outfile)
        
        nfile += 1

    fFiles.close()


if __name__ == '__main__':
    os.chdir('..')
    vgDenoise(5101)
    print 'done'

