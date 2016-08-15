
"""
vg align composites command

Align channels in a composite image and update records in composites.csv,
keeping whitespace and comments intact.
"""

import os
import csv

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg


os.chdir('../..')
csvFiles,fFiles = lib.openCsvReader(config.dbFiles)

csvNew,fNew = lib.openCsvWriter(config.dbCompositesNew)

fComposites = open(config.dbComposites,'rt')
csvComposites = csv.reader(fComposites)
csvComposites.next() # skip header row! #. brittle
targetKey = ''
for row in csvComposites:
    if row==[]:
        csvNew.writerow(row)
    elif row[0][0]=='#':
        csvNew.writerow(row)
    else:
        compositeId = row[config.colCompositesCompositeId]
        fileId = row[config.colCompositesFileId]
        volume = row[config.colCompositesVolume]
        filter = row[config.colCompositesFilter]

        # print fileId
        rowFiles = lib.getJoinRow(csvFiles, config.colFilesFileId, fileId)
        if rowFiles:
            system = rowFiles[config.colFilesSystem]
            craft = rowFiles[config.colFilesCraft]
            target = rowFiles[config.colFilesTarget]
            camera = rowFiles[config.colFilesCamera]

            # build a key
            targetKey = system + '-' + craft + '-' + target + '-' + camera
            # print targetKey
            
        doReplace = False
        if targetKey=='Jupiter-Voyager1-Jupiter-Wide':
            # C1550829 - C1602732 inclusive
            if fileId>='C1550829' and fileId<='C1602732':
                if compositeId!=fileId:
                    doReplace = True

        if doReplace:
            newrow = [fileId, fileId, volume, filter]
            print newrow
            csvNew.writerow(newrow)
        else:
            csvNew.writerow(row)


fNew.close()
fComposites.close()
fFiles.close()

