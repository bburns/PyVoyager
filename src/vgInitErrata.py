
"""
vg init errata command

Initialize the errata.csv file, which contains corrections to the original index files,
which are fed into files.csv.
"""

# this is obsolete/not needed, but might need someday



import os

import config
import lib



def vgInitErrata():
    "Build the errata.csv file based on known problems with index files"

    # open the errata.csv file
    csvErrata, fErrata = lib.openCsvWriter(config.dbErrata)
    fields = 'fileId,fieldname,newvalue'.split(',') # keep in synch with row, below
    csvErrata.writerow(fields)

    # iterate over all image files
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)

    for row in csvFiles:
        # get field values
        # volume,fileid,phase,craft,target,time,instrument,filter,note
        fileId = row[config.colFilesFileId] # eg C1385455
        time = row[config.colFilesTime] # eg UNKNOWN
        # if debug: print 'row',row[:-1] # skip note

        outRow = None

        # # 1529 of these
        # if time[0]=='U': # UNKNOWN or UNK
        #     outRow = [fileId,'time','unknown'] # keep in sync with fields, above

        # # 349 of these
        # elif time[:7]=='1978-01':
        #     time = '1979-01' + time[7:]
        #     outRow = [fileId,'time',time] # keep in sync with fields, above

        if outRow:
            print outRow
            csvErrata.writerow(outRow)

    fFiles.close()
    fErrata.close()


if __name__ == '__main__':
    os.chdir('..')
    vgInitErrata()
    print 'done'


