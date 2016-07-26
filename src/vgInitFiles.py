
# vg init files command
# build the files.csv table from the VGISS index files
# files.csv lists ALL available voyager images


import os
import csv

import config
import lib



def initFiles():
    "Build the files table (files.csv) from the VGISS index files (rawimages_*.tab)"

    # iterate down the giant csv files
    # get the fileid, craft, flyby, target, camera
    # write to files.csv

    # open files.csv for writing
    fileout = open(config.filesdb, 'wb')
    # IMPORTANT: keep fields in synch with row, below, and config.filesCol*
    fields = 'volume,fileid,phase,craft,target,time,instrument,filter,note'.split(',')
    writer = csv.writer(fileout)
    writer.writerow(fields)

    # iterate over rawimages_* files in index folder
    for root, dirs, files in os.walk(config.indexFolder):
        for filename in files:
            if filename[:10]=='RAWIMAGES_' and filename[-3:]=='TAB':
                filepath = config.indexFolder + filename
                print 'reading', filepath
                filein = open(filepath, 'rt')
                reader = csv.reader(filein)
                for row in reader:
                    row = [field.strip() for field in row]

                    # get field values
                    volume = row[config.indexFileColVolume] # eg VGISS_5101
                    filename = row[config.indexFileColFilename] # eg C1385455_RAW.IMG
                    craft = row[config.indexFileColCraft] # eg VOYAGER 1
                    phase = row[config.indexFileColPhase] # eg JUPITER ENCOUNTER
                    target = row[config.indexFileColTarget] # eg N RINGS
                    time = row[config.indexFileColTime] # eg 1979-03-05T15:32:56
                    instrument = row[config.indexFileColInstrument] # eg NARROW ANGLE CAMERA
                    filter = row[config.indexFileColFilter] # eg ORANGE
                    note = row[config.indexFileColNote]

                    # translate where needed
                    volume = volume[-4:] # eg 5101
                    fileid = filename.split('_')[0] # eg C1385455
                    phase = config.indexTranslations[phase] # eg Jupiter
                    craft = config.indexTranslations[craft] # eg Voyager1
                    instrument = config.indexTranslations[instrument] # eg Narrow
                    target = target.title().replace(' ','_') # eg N_Rings

                    # handle rings specially - don't want them to become separate movies -
                    # include them with the planet
                    # but just include for the wide-angle camera - otherwise too many
                    if target[2:]=='Rings' and instrument=='Wide':
                        planetLetter = target[:1]
                        if planetLetter=='J': target='Jupiter'
                        elif planetLetter=='S': target='Saturn'
                        elif planetLetter=='U': target='Uranus'
                        elif planetLetter=='N': target='Neptune'

                    filter = filter.title() # eg Orange

                    # write row
                    # IMPORTANT: keep row in sync with fields, above
                    row = [volume, fileid, phase, craft, target, time, instrument, filter, note]
                    # print row # too slow
                    writer.writerow(row)

                filein.close()

    fileout.close()



if __name__ == '__main__':
    os.chdir('..')
    initFiles()
    print 'done'

