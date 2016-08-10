
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
def vgAdjust(filterVolume, optionOverwrite=False, directCall=True):
    "Build adjusted images for given volume, if they don't exist yet"

    filterVolume = str(filterVolume) # eg '5101'
    imagesSubfolder = config.imagesFolder + 'VGISS_' + filterVolume + '/'
    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + filterVolume + '/'

    # quit if volume folder exists
    if os.path.isdir(adjustmentsSubfolder) and optionOverwrite==False:
        if directCall:
            print "Folder exists - skipping vg images step: " + centersubfolder
        return

    # build the plain images for the volume, if not already there
    if filterVolume!='':
        vgConvert.vgConvert(filterVolume, False, False)

        # make new folder
        lib.rmdir(adjustmentsSubfolder)
        lib.mkdir(adjustmentsSubfolder)

    # get number of files to process
    nfiles = len(os.listdir(imagesSubfolder))

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)
    nfile = 1
    for row in csvFiles:
        volume = row[config.filesColVolume]
        if volume!=filterVolume: continue # filter on desired volume

        fileId = row[config.filesColFileId]
        filter = row[config.filesColFilter]
        system = row[config.filesColPhase]
        craft = row[config.filesColCraft]
        target = row[config.filesColTarget]
        camera = row[config.filesColInstrument]

        # adjust the file
        pngFilename = fileId + '_' + config.imageType + '_' + filter + '.png'
        infile = imagesSubfolder + pngFilename
        outfile = lib.getAdjustedFilepath(volume, fileId, filter)
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




