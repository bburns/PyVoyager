
# build the files.txt table

import os # for system
import csv

import config
import lib

        

def buildFilesTable():
    "build the files table (files.txt) from the cumulative index file (cumindex.tab)"
    
    # iterate down the giant csv file
    # get the craft, flyby, target, camera
    
    filein = open(config.indexfile, 'rt')
    fileout = open(config.filesdb, 'wb')
    i = 1
    fields = 'fileid,filetitle,phase,craft,target,instrument,filter,note'.split(',') # keep in synch with row, below
    try:
        reader = csv.reader(filein)
        writer = csv.writer(fileout)
        writer.writerow(fields)
        for row in reader:
            filename = row[config.col_filename].strip()
            # ext = filename.split('.')[1]
            
            # get image files
            # if ext=='IMG':
            if True:
                
                # get field values
                # filetype = row[config.col_filetype].strip()
                craft = row[config.col_craft].strip()
                phase = row[config.col_phase].strip()
                target = row[config.col_target].strip()
                instrument = row[config.col_instrument].strip()
                filter = row[config.col_filter].strip()
                note = row[config.col_note].strip()
                
                # translate field values
                # filetype = config.translations[filetype]
                craft = config.translations[craft]
                phase = config.translations[phase]
                target = target.title() # titlecase
                instrument = config.translations[instrument]
                
                # add filter name, as added by img2png
                # filename = filename.split('.')[0] + '_' + filter + '.PNG' # eg centered_foo_ORANGE.PNG
                
                filetitle = filename.split('_')[0]
                fileid = 'file' + str(i)
                row = [fileid, filetitle, phase, craft, target, instrument, filter, note] # keep in sync with fields, above
                # print row
                writer.writerow(row)
                
                i += 1
                
    finally:
        filein.close()
        fileout.close()
    
    

if __name__ == '__main__':
    buildFilesTable()
    
                
    
    
