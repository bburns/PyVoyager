
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

import vgAdjust



def vgCenter(buildVolnum='', buildImageId='', overwrite=False, directCall=True):
    "Build centered images for given volume, if they don't exist yet"

    buildVolnum = str(buildVolnum) # eg '5101'
    buildImageId = buildImageId.upper() # always capital C
    
    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + buildVolnum + '/'
    centersSubfolder = config.centersFolder + 'VGISS_' + buildVolnum + '/'

    if os.path.isdir(centersSubfolder) and overwrite==False:
        if directCall:
            print "Folder exists - skipping vg centers step: " + centersSubfolder
    else:
        # build the adjusted images for the volume, if not already there
        if buildVolnum!='':
            vgAdjust.vgAdjust(buildVolnum, False, False)

        # if we're building an entire volume, remove the existing directory first
        if buildVolnum!='':
            lib.rmdir(centersSubfolder)
            lib.mkdir(centersSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(adjustmentsSubfolder))

        # read small dbs into memory
        centeringInfo = lib.readCsv(config.dbCentering) # when to turn centering on/off
        targetInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

        # iterate through all available images, filter on desired volume
        csvFiles, fFiles = lib.openCsvReader(config.dbFiles)

        # join on centers.csv file
        csvCenters, fCenters = lib.openCsvReader(config.dbCenters)
        csvCenters.next() # skip header row #. brittle
        # fileIdCenters = lib.nextRow(csvCenters, config.colCentersFileId)

        # join on centersOverride.csv file
        csvCentersOverride, fCentersOverride = lib.openCsvReader(config.dbCentersOverride)
        csvCentersOverride.next() # skip header row #. brittle

        nfile = 1
        for rowFiles in csvFiles:
            volume = rowFiles[config.colFilesVolume]
            fileId = rowFiles[config.colFilesFileId]

            if volume==buildVolnum or fileId==buildImageId:

                # get image properties
                filter = rowFiles[config.colFilesFilter]
                system = rowFiles[config.colFilesSystem]
                craft = rowFiles[config.colFilesCraft]
                target = rowFiles[config.colFilesTarget]
                camera = rowFiles[config.colFilesCamera]

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
                                                        config.colCentersFileId, fileId)
                    if rowCentersOverride:
                        print 'found centers override record - using x,y from that'
                        print rowCentersOverride
                        x = int(rowCentersOverride[config.colCentersX])
                        y = int(rowCentersOverride[config.colCentersY])
                        # radius = int(rowCentersOverride[config.colCentersRadius])
                    else:
                        rowCenters = lib.getJoinRow(csvCenters,
                                                    config.colCentersFileId, fileId)
                        if rowCenters:
                            # print 'found centers record - using that'
                            # print rowCenters
                            x = int(rowCenters[config.colCentersX])
                            y = int(rowCenters[config.colCentersY])
                        else:
                            print 'record not found'
                # center image file (if x,y==399,399 will just copy the file to center folder)
                libimg.centerImageFileAt(infile, outfile, x, y)

        fCentersOverride.close()
        fCenters.close()
        fFiles.close()


if __name__ == '__main__':
    os.chdir('..')
    vgCenter('','C1540858')
    print 'done'



