
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



#. handle indiv imageids
# def vgDenoise(buildVolnum='', buildImageId='', overwrite=False, directCall=True):
# def vgDenoise(buildVolnum='', buildImageId='', targetPath=None, overwrite=False, directCall=True):
# def vgDenoise(buildVolnum='', buildImageId='', targetPath=None, options={}, directCall=True):
def vgDenoise(volnum='', overwrite=False, directCall=True):
    
    "remove noise from images in given volume"

    volnum = str(volnum) # eg '5101'
    # buildImageId = buildImageId.upper() # always capital C
    # overwrite = options.get('overwrite') # True or None
    # adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + volnum + '/'
    # denoisedSubfolder = config.denoisedFolder + 'VGISS_' + volnum + '/'
    inputSubfolder = lib.getSubfolder('adjust', filterVolume)
    outputSubfolder = lib.getSubfolder('denoise', filterVolume)

    if volnum!='':
        # quit if volume folder exists
        # if os.path.isdir(denoisedSubfolder) and overwrite==False:
        if os.path.isdir(outputSubfolder) and overwrite==False:
            if directCall:
                # print "Folder exists - skipping vg denoise step: " + denoisedSubfolder
                print "Folder exists - skipping vg denoise step: " + outputSubfolder
            return

        # build the adjusted images for the volume, if not already there
        #. handle indiv images also - could lookup volume by fileid, call vgadjust here
        vgAdjust.vgAdjust(volnum, False, False) # not a direct call by user
        
        # make folder
        # lib.rmdir(denoisedSubfolder)
        # os.mkdir(denoisedSubfolder)
        lib.mkdir(outputSubfolder)


    # get number of files to process
    nfiles = len(os.listdir(inputSubfolder))

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

        # get filenames
        # infile = lib.getAdjustedFilepath(volume, fileId, filter)
        # outfile = lib.getDenoisedFilepath(volume, fileId, filter)
        infile = lib.getFilepath('adjust', volume, fileId, filter)
        outfile = lib.getFilepath('denoise', volume, fileId, filter)

        # print 'Volume %s denoising %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
        log.logr('Volume %s denoising %d/%d: %s' % (volume,nfile,nfiles,infile))
        
        libimg.denoiseImageFile(infile, outfile)
        
        nfile += 1

    fFiles.close()


if __name__ == '__main__':
    os.chdir('..')
    vgDenoise(5101)
    print 'done'

