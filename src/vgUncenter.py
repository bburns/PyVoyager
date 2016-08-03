
"""
vg uncenter command

after updating centering.csv, run this command to uncenter images at closest approach.
this will basically copy the images from the images step into the appropriate centers folder.
saves the step of recentering all the volumes.
"""

#. renamed from vg update centers command - handle arguments

import csv
import os
import os.path

import config
import lib
import libimg
import db


def vgUncenter(volnum):
    "Uncenter images for the given volume based on records in db/centering.csv"

    volnum = str(volnum) # eg '5101'
    print 'Uncentering images in volume', volnum

    imagesubfolder = config.imagesFolder + 'VGISS_' + volnum + '/'
    centersubfolder = config.centersFolder + 'VGISS_' + volnum + '/'

    # read small db into memory - tells when to turn centering on/off
    centeringInfo = lib.readCsv(config.centeringdb)

    # iterate through all available images, filter on desired volume
    reader, f = lib.openCsvReader(config.filesdb)
    for row in reader:
        volume = row[config.filesColVolume]
        if volume==volnum:
            fileId = row[config.filesColFileId]
            filter = row[config.filesColFilter]
            system = row[config.filesColPhase]
            craft = row[config.filesColCraft]
            target = row[config.filesColTarget]
            camera = row[config.filesColInstrument]

            # get the centering info, if any
            # info includes planetCraftTargetCamera,centeringOff,centeringOn
            # planetCraftTargetCamera = system + craft + target + camera
            planetCraftTargetCamera = system + '-' + craft + '-' + target + '-' + camera
            centeringInfoRecord = centeringInfo.get(planetCraftTargetCamera)
            if centeringInfoRecord:
                centeringOff = centeringInfoRecord['centeringOff']
                centeringOn = centeringInfoRecord['centeringOn']
                docenter = fileId<centeringOff or fileId>centeringOn
            else: # if no info for this target just center it
                docenter = True

            # uncenter the file if necessary
            if docenter==False:
                pngfilename = fileId + '_' + config.imageType + '_' + filter + '.png'
                infile = imagesubfolder + pngfilename
                if os.path.isfile(infile):
                    outfile = centersubfolder + config.centersPrefix + pngfilename
                    print 'Uncentering %s              \r' % (outfile),
                    libimg.adjustImageFile(infile, outfile, docenter)
                else:
                    print 'Warning: missing image file', infile
    f.close()
    print


if __name__ == '__main__':
    os.chdir('..')
    vgUncenter(5101)
    print 'done'



