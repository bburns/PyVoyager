
"""
vg init files command

Build the files.csv table from the VGISS index files.
files.csv lists ALL available voyager images.
"""

import os
import csv

import config
import lib



def vgInitFiles():
    "Build the files table (files.csv) from the VGISS index files (rawimages_*.tab)"

    # iterate down the giant csv files
    # get the fileid, craft, flyby, target, camera
    # write to files.csv

    # open files.csv for writing
    # IMPORTANT: keep fields in synch with row, below, and config.filesCol*
    # fileout = open(config.dbFiles, 'wb')
    # writer = csv.writer(fileout)
    writer, fileout = lib.openCsvWriter(config.dbFiles)
    # fields = 'volume,fileid,phase,craft,target,time,instrument,filter,note'.split(',')
    fields = 'fileid,volume,phase,craft,target,time,instrument,filter,note'.split(',')
    writer.writerow(fields)

    # order of planets is so fileIds will be in order
    # see http://pds-rings.seti.org/voyager/iss/calib_images.html
    for planet in [8,5,7,6]:
        filename = 'RAWIMAGES_' + str(planet) + '.TAB'
        filepath = config.indexFolder + filename
        print 'reading', filepath
        filein = open(filepath, 'rt')
        reader = csv.reader(filein)
        for row in reader:
            row = [field.strip() for field in row]

            # get field values
            volume = row[config.colIndexVolume] # eg VGISS_5101
            filename = row[config.colIndexFilename] # eg C1385455_RAW.IMG
            craft = row[config.colIndexCraft] # eg VOYAGER 1
            phase = row[config.colIndexPhase] # eg JUPITER ENCOUNTER
            target = row[config.colIndexTarget] # eg N RINGS
            time = row[config.colIndexTime] # eg 1979-03-05T15:32:56
            instrument = row[config.colIndexInstrument] # eg NARROW ANGLE CAMERA
            filter = row[config.colIndexFilter] # eg ORANGE
            note = row[config.colIndexNote]

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
            # row = [volume, fileid, phase, craft, target, time, instrument, filter, note]
            row = [fileid, volume, phase, craft, target, time, instrument, filter, note]
            # print row # too slow
            writer.writerow(row)

        filein.close()

    fileout.close()



if __name__ == '__main__':
    os.chdir('..')
    vgInitFiles()
    print 'done'

