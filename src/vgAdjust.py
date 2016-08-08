
"""
vg adjust command

Build adjusted images from plain png images.

For now this just means stretching the CALIB images histograms and rotating 180 degrees.
In future could adjust the RAW images by removing reseau marks and dark current images, etc,
maybe sharpening.
"""

import csv
import os
import os.path

import config
import lib
import libimg

import vgConvert


#. handle indiv images also
def vgAdjust(volnum, overwrite=False, directCall=True):
    "Build adjusted images for given volume, if they don't exist yet"

    volnum = str(volnum) # eg '5101'

    imagesSubfolder = config.imagesFolder + 'VGISS_' + volnum + '/'
    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + volnum + '/'

    if os.path.isdir(adjustmentsSubfolder) and overwrite==False:
        if directCall:
            print "Folder exists - skipping vg images step: " + centersubfolder
    else:
        # build the plain images for the volume, if not already there
        if volnum!='':
            vgConvert.vgConvert(volnum, False, False)

        # make new folder
        lib.rmdir(adjustmentsSubfolder)
        lib.mkdir(adjustmentsSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(imagesSubfolder))

        # iterate through all available images, filter on desired volume
        csvFiles, fFiles = lib.openCsvReader(config.filesdb)
        nfile = 1
        for row in csvFiles:
            volume = row[config.filesColVolume]
            if volume==volnum:
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
    # vgAdjust(5101)
    print 'done'




