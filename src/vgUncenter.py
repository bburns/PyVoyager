
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


def vgUncenter(filterVolume):
    "Uncenter images for the given volume based on records in db/centering.csv"

    filterVolume = str(filterVolume) # eg '5101'
    print 'Uncentering images in volume', filterVolume

    # imagesubfolder = config.imagesFolder + 'VGISS_' + filterVolume + '/'
    # centersubfolder = config.centersFolder + 'VGISS_' + filterVolume + '/'
    inputSubfolder = lib.getFolder('convert', filterVolume)
    outputSubfolder = lib.getFolder('center', filterVolume)

    # read small db into memory - tells when to turn centering on/off
    centeringInfo = lib.readCsv(config.dbCentering)

    # iterate through all available images, filter on desired volume
    reader, f = lib.openCsvReader(config.dbFiles)
    for row in reader:
        volume = row[config.colFilesVolume]
        if volume==filterVolume:
            fileId = row[config.colFilesFileId]
            filter = row[config.colFilesFilter]
            system = row[config.colFilesSystem]
            craft = row[config.colFilesCraft]
            target = row[config.colFilesTarget]
            camera = row[config.colFilesCamera]

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
                infile = inputSubfolder + pngfilename
                if os.path.isfile(infile):
                    outfile = outputSubfolder + config.centersPrefix + pngfilename
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



