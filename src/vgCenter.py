
"""
vg center command

Build centered and stabilized images from adjusted images using centers.csv
and centersOverride.csv.

See also vgInitCenters.py

"""

import csv
import os
import os.path

import config
import lib
import libimg
import db

import vgAdjust




def vgCenter(buildVolnum='', buildImageId='', overwrite=False, directCall=True):
    "Build centered images for given volume, if they don't exist yet"

    buildImageId = buildImageId.upper() # always capital C
    
    #. need to handle indiv imageids? what would stabilization mean then though?
    # if buildVolnum=='': return

    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + str(buildVolnum) + '/'
    centersSubfolder = config.centersFolder + 'VGISS_' + str(buildVolnum) + '/'

    if os.path.isdir(centersSubfolder) and overwrite==False:
        if directCall:
            print "Folder exists - skipping vg centers step: " + centersSubfolder
    else:
        buildVolnum = str(buildVolnum) # eg '5101'
    
        # build the adjusted images for the volume, if not already there
        if buildVolnum!='':
            vgAdjust.vgAdjust(buildVolnum, False, False)

        # if we're building an entire volume, remove the existing directory first
        if buildVolnum!='':
            lib.rmdir(centersSubfolder)
            os.mkdir(centersSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(adjustmentsSubfolder))

        # read small dbs into memory
        centeringInfo = lib.readCsv(config.centeringdb) # when to turn centering on/off
        targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

        # iterate through all available images, filter on desired volume
        csvFiles, fFiles = lib.openCsvReader(config.filesdb)

        # join on centers.csv file
        csvCenters, fCenters = lib.openCsvReader(config.centersdb)
        csvCenters.next() # skip header row #. brittle
        # fileIdCenters = lib.nextRow(csvCenters, config.centersColFileId)

        # join on centersOverride.csv file
        csvCentersOverride, fCentersOverride = lib.openCsvReader(config.dbCentersOverride)
        csvCentersOverride.next() # skip header row #. brittle

        i = 0
        nfile = 1
        for rowFiles in csvFiles:
            if rowFiles==[] or rowFiles[0][0]=="#": continue # skip blank lines and comments
            if i==0: fields = rowFiles
            else:
                volume = rowFiles[config.filesColVolume]
                fileId = rowFiles[config.filesColFileId]
                
                if volume==buildVolnum or fileId==buildImageId:

                    # get image properties
                    filter = rowFiles[config.filesColFilter]
                    system = rowFiles[config.filesColPhase]
                    craft = rowFiles[config.filesColCraft]
                    target = rowFiles[config.filesColTarget]
                    camera = rowFiles[config.filesColInstrument]

                    # relabel target field if necessary
                    target = lib.retarget(targetInfo, fileId, target)

                    # get filenames
                    infile = lib.getAdjustedFilepath(volume, fileId, filter)
                    outfile = lib.getCenteredFilepath(volume, fileId, filter)

                    # print 'Volume %s centering %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
                    print 'Volume %s centering %d/%d: %s' % (volume,nfile,nfiles,infile)
                    nfile += 1

                    targetKey = system + '-' + craft + '-' + target + '-' + camera

                    # do we actually need to center this image?
                    doCenter = lib.centerThisImageQ(centeringInfo, targetKey, fileId, target)

                    x,y = 399,399
                    if doCenter:
                        # get x,y = from joined file
                        rowCentersOverride = lib.getJoinRow(csvCentersOverride,
                                                            config.centersColFileId, fileId)
                        if rowCentersOverride:
                            print 'found centers override record - using x,y from that'
                            print rowCentersOverride
                            x = int(rowCentersOverride[config.centersColX])
                            y = int(rowCentersOverride[config.centersColY])
                            # radius = int(rowCentersOverride[config.centersColRadius])
                        else:
                            rowCenters = lib.getJoinRow(csvCenters,
                                                        config.centersColFileId, fileId)
                            if rowCenters:
                                # print 'found centers record - using that'
                                # print rowCenters
                                x = int(rowCenters[config.centersColX])
                                y = int(rowCenters[config.centersColY])
                            else:
                                print 'record not found'
                    # center image file (if x,y==399,399 will just copy the file to center folder)
                    libimg.centerImageFileAt(infile, outfile, x, y)
                            
            i += 1

        fCentersOverride.close()
        fCenters.close()
        fFiles.close()


if __name__ == '__main__':
    os.chdir('..')
    vgCenter('','C1540858')
    print 'done'



