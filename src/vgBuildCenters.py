
# vg centers command
# build centered images from plain png images

import csv
import os
import os.path

import config
import lib
import libimg
import db

import vgBuildImages


def buildCenters(volnum, overwrite=False):
    "Build centered images for given volume, if they don't exist yet"

    imagesubfolder = config.imagesFolder + 'VGISS_' + str(volnum) + '/'
    centersubfolder = config.centersFolder + 'VGISS_' + str(volnum) + '/'

    if int(volnum)==0: # test volume - turn on image debugging
        config.drawBoundingBox = True
        config.drawCircle = True
        config.drawCrosshairs = True

    # for test (vol=0), can overwrite test folder
    if int(volnum)!=0 and os.path.isdir(centersubfolder) and overwrite==False:
        print "Folder exists - skipping vg images step: " + centersubfolder
    else:
        # build the plain images for the volume, if not already there
        vgBuildImages.buildImages(volnum)

        # make new folder
        lib.rmdir(centersubfolder)
        lib.mkdir(centersubfolder)

        # read small db into memory - tells when to turn centering on/off
        centeringInfo = lib.readCsv('db/centering.csv')

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

                    # center the file
                    pngfilename = fileId + '_' + config.imageType + '_' + filter + '.png'
                    infile = imagesubfolder + pngfilename
                    outfile = centersubfolder + config.centersPrefix + pngfilename
                    # print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                    print 'centering %d: %s     \r' %(nfile,infile),
                    if os.path.isfile(infile):
                        libimg.adjustImageFile(infile, outfile, docenter)
                    else:
                        print 'Warning: missing image file', infile

                    nfile += 1

            i += 1

        f.close()

        print

if __name__ == '__main__':
    os.chdir('..')
    buildCenters(0)
    print 'done'



