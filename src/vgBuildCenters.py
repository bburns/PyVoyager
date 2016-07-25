
# vg centers command
# build centered images from adjusted images

import csv
import os
import os.path

import config
import lib
import libimg
import db

import vgBuildAdjustments


def buildCenters(volnum, overwrite=False):
    "Build centered images for given volume, if they don't exist yet"

    #. need to handle indiv imageids
    if volnum=='': return

    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + str(volnum) + '/'
    centersSubfolder = config.centersFolder + 'VGISS_' + str(volnum) + '/'

    if int(volnum)==0: # test volume - turn on image debugging
        config.drawBoundingBox = True
        config.drawCircle = True
        config.drawCrosshairs = True

    # for test (vol=0), can overwrite test folder
    if int(volnum)!=0 and os.path.isdir(centersSubfolder) and overwrite==False:
        # print "Folder exists - skipping vg centers step: " + centersSubfolder
        pass
    else:
        # build the adjusted images for the volume, if not already there
        vgBuildAdjustments.buildAdjustments(volnum)

        # make new folder
        lib.rmdir(centersSubfolder)
        lib.mkdir(centersSubfolder)

        # get number of files to process
        # root, dirs, files = os.walk(adjustmentsSubfolder)
        # nfiles = len(files)

        # read small db into memory - tells when to turn centering on/off
        centeringInfo = lib.readCsv(config.centeringdb)

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

                    if docenter:
                        # center the file
                        adjustedFilename = config.adjustmentsPrefix + fileId + '_' + \
                                      config.imageType + '_' + filter + '.png'
                        infile = adjustmentsSubfolder + adjustedFilename
                        centeredFilename = config.centersPrefix + adjustedFilename[9:] # remove 'adjusted_'
                        # outfile = centersSubfolder + config.centersPrefix + pngfilename
                        outfile = centersSubfolder + centeredFilename
                        # print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                        print 'Centering %d: %s     \r' %(nfile,infile),
                        # print 'Centering %d/%d: %s     \r' %(nfile,nfilesinfile),
                        if os.path.isfile(infile):
                            libimg.centerImageFile(infile, outfile)
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



