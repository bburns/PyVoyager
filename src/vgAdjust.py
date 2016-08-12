
"""
vg adjust command

Build adjusted images from plain png images.

For now this just means stretching the CALIB images histograms and rotating 180 degrees.
"""

import csv
import os
import os.path

import config
import lib
import libimg

import vgConvert


#. handle indiv images also
# def vgAdjust(volnum, imageId=None, targetPath=None, overwrite=False, directCall=True):
# def vgAdjust(volnum, overwrite=False, directCall=True):
# def vgAdjust(filterVolume, optionOverwrite=False, directCall=True):
def vgAdjust(filterVolume='', filterImageId='', optionOverwrite=False, directCall=True):

    "Build adjusted images for given volume, if they don't exist yet"

    filterVolume = str(filterVolume) # eg '5101'
    # imagesSubfolder = config.imagesFolder + 'VGISS_' + filterVolume + '/'
    # adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + filterVolume + '/'
    # imagesSubfolder = lib.getSubfolder('convert', filterVolume)
    # adjustmentsSubfolder = lib.getSubfolder('adjust', filterVolume)

    if filterVolume!='':

        inputSubfolder = lib.getSubfolder('convert', filterVolume)
        outputSubfolder = lib.getSubfolder('adjust', filterVolume)

        # quit if volume folder exists
        # if os.path.isdir(adjustmentsSubfolder) and optionOverwrite==False:
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return

        # build the plain images for the volume, if not already there
        vgConvert.vgConvert(filterVolume, optionOverwrite=False, directCall=False)

        # make new folder
        lib.mkdir(outputSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(inputSubfolder))
    else:
        nfiles = 1

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for row in csvFiles:
        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]

        # if volume!=filterVolume: continue # filter on desired volume
        if volume!=filterVolume and fileId!=filterImageId: continue # filter on desired volume

        filter = row[config.colFilesFilter]
        system = row[config.colFilesSystem]
        craft = row[config.colFilesCraft]
        target = row[config.colFilesTarget]
        camera = row[config.colFilesCamera]

        # adjust the file
        # pngFilename = fileId + '_' + config.imageType + '_' + filter + '.png'
        # infile = imagesSubfolder + pngFilename
        # outfile = lib.getAdjustedFilepath(volume, fileId, filter)
        infile = lib.getFilepath('convert', volume, fileId, filter)
        outfile = lib.getFilepath('adjust', volume, fileId, filter)
        print 'Volume %s adjusting %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
        if os.path.isfile(infile):
            libimg.adjustImageFile(infile, outfile)
        else:
            print 'Warning: missing image file', infile
        nfile += 1

    fFiles.close()
    print

if __name__ == '__main__':
    os.chdir('..')
    vgAdjust(5101)
    print 'done'


