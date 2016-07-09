
# build the files.txt table from the VGISS index files
# files.txt lists ALL available voyager images


import os
import csv

import config
import lib

        

def initFiles():
    "build the files table (files.txt) from the VGISS index files (rawimages_*.tab)"
    
    # iterate down the giant csv files
    # get the fileid, craft, flyby, target, camera
    # write to files.txt
    
    fileout = open(config.filesdb, 'wb')
    fields = 'volume,fileid,phase,craft,target,instrument,filter,note'.split(',') # keep in synch with row, below
    writer = csv.writer(fileout)
    writer.writerow(fields)
    
    # iterate over rawimages_* files in index folder
    for root, dirs, files in os.walk(config.indexFolder):
        for filename in files:
            if filename[:10]=='RAWIMAGES_' and filename[-3:]=='TAB':
                filepath = config.indexFolder + '/' + filename
                print 'reading', filepath
                filein = open(filepath, 'rt')
                reader = csv.reader(filein)
                for row in reader:
                    row = [field.strip() for field in row]

                    # get field values
                    volume = row[config.colVolume] # eg VGISS_5101
                    filename = row[config.colFilename] # eg C1385455_RAW.IMG
                    craft = row[config.colCraft] # eg VOYAGER 1
                    phase = row[config.colPhase] # eg JUPITER ENCOUNTER
                    target = row[config.colTarget].title() # eg IO
                    instrument = row[config.colInstrument] # eg NARROW ANGLE CAMERA
                    filter = row[config.colFilter] # eg ORANGE
                    note = row[config.colNote] 

                    fileid = filename.split('_')[0] # eg C1385455
                    
                    # translate where needed
                    phase = config.indexTranslations[phase] # eg Jupiter
                    craft = config.indexTranslations[craft] # eg Voyager1
                    instrument = config.indexTranslations[instrument] # eg Narrow

                    # write row
                    row = [volume, fileid, phase, craft, target, instrument, filter, note] # keep in sync with fields, above
                    # print row # too slow
                    writer.writerow(row)

                filein.close()
                
    fileout.close()



if __name__ == '__main__':
    initFiles()
    print 'done'
    
                
    
    
