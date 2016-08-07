
"""
vg center command

Currently this stabilizes images within a volume - ideally it would distribute
the images to their targets and then stabilize on that sequence, but this works
fairly well, with possible discontinuities at volume boundaries.

Build centers.csv file for a volume by centering and stablizing images in files.csv.
"""

import os
import os.path

import config
import lib
import libimg
import log

import vgAdjust


config.drawCrosshairs = True
config.drawTarget = True


# def vgCenter(volnum, overwrite=False, directCall=True):
def vgCenter(buildVolnum='', buildImageId='', overwrite=False, directCall=True):
    "Build centered and stabilized images for given volume and write x,y,radius to centers.csv"

    buildVolnum = str(buildVolnum) # eg '5101'
    buildImageId = buildImageId.upper() # always capital C

    #. need to handle indiv imageids - stabilize to the target disc.
    #. but should fine tune in relation to previous image,
    # so would want to remember that for the target sequence.

    # #. if file contains the given volume, either stop or remove those lines
    # s = ',' + volnum + ','
    # if lib.fileContainsString(config.centersdb, s):
    #     if overwrite:
    #         lib.removeLinesFromFile(config.centersdb, s)
    #     else:
    #         print 'Centers.csv already contains volume ' + volnum + ' - run with -y to overwrite'
    #         return

    adjustmentsSubfolder = config.adjustmentsFolder + 'VGISS_' + buildVolnum + '/'
    centersSubfolder = config.centersFolder + 'VGISS_' + buildVolnum + '/'

    if buildVolnum!='' and os.path.isdir(centersSubfolder) and overwrite==False:
        if directCall:
            print "Folder exists - skipping vg center step: " + centersSubfolder
        return

    # build the adjusted images for the volume, if not already there
    #. handle indiv images also - could lookup volume by fileid, call vgadjust here
    if buildVolnum!='':
        vgAdjust.vgAdjust(buildVolnum, False, False)
        
    # if we're building an entire volume, remove the existing directory first
    if buildVolnum!='':
        lib.rmdir(centersSubfolder)
        lib.mkdir(centersSubfolder)

    # get number of files to process
    nfiles = len(os.listdir(adjustmentsSubfolder))

    # read small dbs into memory
    centeringInfo = lib.readCsv(config.centeringdb) # when to turn centering on/off
    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

    # iterate through all available images, filter on desired volume
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)

    # open centers_new.csv file to write any new records to
    csvNewCenters, fNewCenters = lib.openCsvWriter(config.newcentersdb)

    # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
    lastImageInTargetSequence = {}

    # open positions.csv file for target angular size info
    csvPositions, fPositions = lib.openCsvReader(config.positionsdb)

    nfile = 1
    for rowFiles in csvFiles:
        volume = rowFiles[config.filesColVolume]
        fileId = rowFiles[config.filesColFileId]
        
        # if volume!=volnum: continue # filter to given volume
        # if volume==buildVolnum or fileId==buildImageId:
        if volume!=buildVolnum and fileId!=buildImageId: continue # filter to given volume/image

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
        log.logr('Volume %s centering %d/%d: %s' % (volume,nfile,nfiles,infile))
        nfile += 1

        targetKey = system + '-' + craft + '-' + target + '-' + camera

        # do we actually need to center this image?
        doCenter = lib.centerThisImageQ(centeringInfo, targetKey, fileId, target)

        if doCenter:

            # print
            # print 'currentimage',volume,fileId,filter,targetKey

            # for this target sequence (eg ariel flyby), what was the last good image?
            # use that as a fixed image against which we try to align the current image.
            lastImageRecord = lastImageInTargetSequence.get(targetKey)
            if lastImageRecord:
                fixedfile = lastImageRecord[0]
                ntimesused = lastImageRecord[1]
                lastImageInTargetSequence[targetKey][1] += 1 # ntimes used
                # log.log('aligning to', fixedfile)
            else:
                fixedfile = None
                ntimesused = 0
                # log.log('no image to align to yet for',targetKey)

            # get expected radius
            rowPositions = lib.getJoinRow(csvPositions, config.positionsColFileId, fileId)
            if rowPositions:
                # fraction of frame
                imageFraction = float(rowPositions[config.positionsColImageFraction])
                targetRadius = int(400*imageFraction) #.param
            else:
                targetRadius = 0 # just rhea

            # find center of target using blob and hough, then align to fixedimage.
            # lastRadius and radiusFound are used to determine if it has changed 'too much'.
            x,y,foundRadius = libimg.centerImageFile(infile, outfile, targetRadius)
            x,y,stabilizationOk = libimg.stabilizeImageFile(outfile, outfile,
                                                            targetRadius, x,y,foundRadius)
            # remember first image in sequence
            if fixedfile is None:
                fixedfile = outfile
                # log.log('first fixed frame', fixedfile, 'targetRadius', targetRadius)
                lastImageInTargetSequence[targetKey] = [fixedfile, 0]

            # if image was successfully stabilized, remember it
            if stabilizationOk and ntimesused >= config.stabilizeNTimesToUseFixedFrame:
                fixedfile = outfile
                # log.log('new fixed frame', fixedfile)
                lastImageInTargetSequence[targetKey] = [fixedfile, 0]

            # write x,y,radius to newcenters file
            rowNew = [fileId, volume, x, y, foundRadius]
            csvNewCenters.writerow(rowNew)

    fPositions.close()
    fNewCenters.close()
    fFiles.close()

    # now append newcenters records to centers file
    if os.path.isfile(config.newcentersdb):
        lib.concatFiles(config.centersdb, config.newcentersdb)
        lib.rm(config.newcentersdb)
        print
        print 'New records appended to centers.csv file - please make sure any older records are removed and the file is sorted before committing it to git'
    else:
        print


if __name__ == '__main__':
    os.chdir('..')
    vgCenter(5101)
    print 'done'

