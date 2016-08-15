
"""
vg merge composites command

merge records in compositesNew.csv into composites.csv,
keeping whitespace and comments the same.
keep existing composites.csv as compositesBackup.csv

"""

import os
import csv
import cv2

import config
import lib
import libimg


import vgCenter
import vgInpaint



def vgMergeComposites():
    """
    """
    # open compositesNew.csv for reading
    csvNew, fNew = lib.openCsvReader(config.dbCompositesNew)

    # open compositesMerged.csv for writing
    csvMerged, fMerged = lib.openCsvWriter(config.dbCompositesMerged)

    # iterate over composites.csv records
    # csvComposites, fComposites = lib.openCsvReader(config.dbComposites)
    # need access to comments and blank lines so don't use openCsvReader
    fComposites = open(config.dbComposites,'rt')
    csvComposites = csv.reader(fComposites)
    csvComposites.next() # skip header row! #. brittle

    for row in csvComposites:

        if row==[]: # blank line
            csvNew.writerow(row)
            continue
        elif row[0][0]=='#': # comment
            csvNew.writerow(row)
            continue
        for row in channelRows:
            csvNew.writerow(row)

        # get composite info
        compositeId = row[config.colCompositesCompositeId]
        fileId = row[config.colCompositesFileId]
        volume = row[config.colCompositesVolume]

        # join on files.csv to get more image properties
        # (note: since compositeId repeats, we might have already advanced to the next record,
        # in which case rowFiles will be None. But the target properties will remain the same.)
        rowFiles = lib.getJoinRow(csvFiles, config.colFilesFileId, compositeId)
        if rowFiles:
            # get file info
            filter = rowFiles[config.colFilesFilter]
            system = rowFiles[config.colFilesSystem]
            craft = rowFiles[config.colFilesCraft]
            target = rowFiles[config.colFilesTarget]
            camera = rowFiles[config.colFilesCamera]
            # relabel target field if necessary - see db/targets.csv for more info
            target = lib.retarget(retargetingInfo, compositeId, target)

        # filter on volume, composite id and targetpath
        volumeOk = (volume==filterVolume if filterVolume else True)
        compositeOk = (compositeId==filterCompositeId if filterCompositeId else True)
        targetPathOk = (lib.targetMatches(targetPathParts, system, craft, target, camera) \
                        if filterTargetPath else True)
        doComposite = (volumeOk and compositeOk and targetPathOk)
        if doComposite:
            # gather image filenames into channelRows so can merge them
            if compositeId == startId:
                channelRows.append(row)
            else:
                # we're seeing a new compositeId, so process all the gathered channels
                printStatus(channelRows,startVol,nfile,startId)
                changed = processChannels(channelRows,optionAlign)
                if optionAlign and changed: writeUpdates(csvNew, channelRows)
                startId = compositeId
                startVol = volume
                channelRows = [row]
                nfile += 1

    # process the last leftover group
    print channelRows
    printStatus(channelRows,startVol,nfile,startId)
    changed = processChannels(channelRows,optionAlign)
    if optionAlign and changed: writeUpdates(csvNew, channelRows)

    print

    fMerged.close()
    fComposites.close()
    fNew.close()


    # rm backup
    # mv existing to backup
    # mv merged to .csv



if __name__ == '__main__':
    os.chdir('..')

    # vgMergeComposites()

