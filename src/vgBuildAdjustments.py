
# vg adjustments command
# build adjusted images from plain png images

# for now this just means stretching the CALIB images histograms and rotating 180degrees.
# in future could adjust the RAW images by removing reseau marks and dark current images, etc.
# maybe sharpening


import csv
import os
import os.path

import config
import lib
import libimg
import db

import vgBuildImages


def buildAdjustments(volnum, overwrite=False):
    "Build adjusted images for given volume, if they don't exist yet"

    imagesSubfolder = config.imagesFolder + 'VGISS_' + str(volnum) + '/'
    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + str(volnum) + '/'

    if int(volnum)==0: # test volume - turn on image debugging
        config.drawBoundingBox = True
        config.drawCircle = True
        config.drawCrosshairs = True

    # for test (vol=0), can overwrite test folder
    if int(volnum)!=0 and os.path.isdir(adjustmentsSubfolder) and overwrite==False:
        # print "Folder exists - skipping vg images step: " + centersubfolder
        pass
    else:
        # build the plain images for the volume, if not already there
        vgBuildImages.buildImages(volnum)

        # make new folder
        lib.rmdir(adjustmentsSubfolder)
        lib.mkdir(adjustmentsSubfolder)

        # get number of files to process
        # root, dirs, files = os.walk(imagesSubfolder)
        # nfiles = len(files)

        # iterate through all available images, filter on desired volume
        f = open(config.filesdb, 'rt')
        i = 0
        reader = csv.reader(f)
        volnum = str(volnum) # eg '5101'
        nfile = 1
        for row in reader:
            if row==[] or row[0][0]=="#": continue # skip blank lines and comments
            if i==0: fields = row
            else:
                volume = row[config.filesColVolume]
                if volume==volnum:
                    fileId = row[config.filesColFileId]
                    filter = row[config.filesColFilter]
                    system = row[config.filesColPhase]
                    craft = row[config.filesColCraft]
                    target = row[config.filesColTarget]
                    camera = row[config.filesColInstrument]

                    # # get the centering info, if any
                    # # info includes planetCraftTargetCamera,centeringOff,centeringOn
                    # # planetCraftTargetCamera = system + craft + target + camera
                    # planetCraftTargetCamera = system + '-' + craft + '-' + target + '-' + camera
                    # centeringInfoRecord = centeringInfo.get(planetCraftTargetCamera)
                    # if centeringInfoRecord:
                    #     centeringOff = centeringInfoRecord['centeringOff']
                    #     centeringOn = centeringInfoRecord['centeringOn']
                    #     docenter = fileId<centeringOff or fileId>centeringOn
                    # else: # if no info for this target just center it
                    #     docenter = True

                    # adjust the file
                    pngfilename = fileId + '_' + config.imageType + '_' + filter + '.png'
                    infile = imagesSubfolder + pngfilename
                    outfile = adjustmentsSubfolder + config.adjustmentsPrefix + pngfilename
                    # print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                    # print 'Centering %d/%d: %s     \r' %(nfile,nfilesinfile),
                    print 'Adjusting %d: %s     \r' %(nfile,infile),
                    if os.path.isfile(infile):
                        libimg.adjustImageFile(infile, outfile)
                    else:
                        print 'Warning: missing image file', infile

                    nfile += 1

            i += 1

        f.close()

        print

if __name__ == '__main__':
    os.chdir('..')
    buildAdjustments(0)
    print 'done'




