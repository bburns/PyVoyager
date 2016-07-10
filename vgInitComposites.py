
# build composites.txt, which will attempt to describe how to combine image channels

# based on image number (~time), filter, target, camera, NOTE field


import os
import csv

import config
import lib

        
# ex composites.txt
# volume,compositeId,centerId,filter,weight
# VGISS_5103,C1537728,C1537728,Blue
# VGISS_5103,C1537728,C1537730,Orange
# VGISS_5103,C1537728,C1537732,Green
# VGISS_5103,C1537734,C1537734,Blue
# VGISS_5103,C1537734,C1537736,Orange
# VGISS_5103,C1537734,C1537738,Green
# VGISS_5103,C1537740,C1537740,Blue
# VGISS_5103,C1537740,C1537742,Orange
# VGISS_5103,C1537740,C1537744,Green
# VGISS_8203,C1027859,C1027859,VIOLET
# VGISS_8203,C1027859,C1027905,GREEN
# VGISS_8203,C1027859,C1027912,ORANGE
# VGISS_8203,C1027937,C1027937,VIOLET
# VGISS_8203,C1027937,C1027943,GREEN
# VGISS_8203,C1027937,C1027950,ORANGE




# from files.txt
# volume,fileid,phase,craft,target,instrument,filter,note
# ['VGISS_5101', 'C1464108', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'UV', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464110', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'BLUE', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE ; 1 OF 4 NA']
# ['VGISS_5101', 'C1464112', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'GREEN', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464114', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'ORANGE', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464330', 'Jupiter', 'Voyager1', 'Europa', 'Narrow', 'CLEAR', 'OPTICAL NAVIGATION']
# ['VGISS_5101', 'C1464337', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'UV', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464339', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'BLUE', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE ; 1 OF 4 NA']
# ['VGISS_5101', 'C1464341', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'GREEN', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464343', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'ORANGE', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464606', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'UV', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464608', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'BLUE', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE ; 1 OF 4 NA']
# ['VGISS_5101', 'C1464610', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'GREEN', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464612', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'ORANGE', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464835', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'UV', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA']
# ['VGISS_5101', 'C1464837', 'Jupiter', 'Voyager1', 'Jupiter', 'Narrow', 'BLUE', 'ROUTINE MULTISPECTRAL LONGITUDE COVERAGE ; 1 OF 4 NA']


def initComposites():
    "build the composites.txt file from likely looking images in files.txt"
    
    # open the composites.txt file
    # fileout = open(config.compositesdb, 'wb')
    # fields = 'volume,compositeId,centerId,filter,weight'.split(',') # keep in synch with row, below
    # writer = csv.writer(fileout)
    # writer.writerow(fields)
    
    # iterate over files
    filein = open(config.filesdb, 'rt')
    reader = csv.reader(filein)
    
    # circular buffer with 7 empty lists - the maximum number of filters in a group we're checking for
    buffer = [[],[],[],[],[],[],[]] 
    i = 0
    
    for row in reader:
        # print row
        if i==0:
            fields = row
        else:
            buffer.pop(0) # remove from front of list
            buffer.append(row) # append item to end of list
        print buffer
        i += 1

        # get field values
        # volume = row[config.indexFileColVolume] # eg VGISS_5101
        # filename = row[config.indexFileColFilename] # eg C1385455_RAW.IMG
        # craft = row[config.indexFileColCraft] # eg VOYAGER 1
        # phase = row[config.indexFileColPhase] # eg JUPITER ENCOUNTER
        # target = row[config.indexFileColTarget].title() # eg IO
        # instrument = row[config.indexFileColInstrument] # eg NARROW ANGLE CAMERA
        # filter = row[config.indexFileColFilter] # eg ORANGE
        # note = row[config.indexFileColNote] 

        # fileid = filename.split('_')[0] # eg C1385455

        # translate where needed
        # phase = config.indexTranslations[phase] # eg Jupiter
        # craft = config.indexTranslations[craft] # eg Voyager1
        # instrument = config.indexTranslations[instrument] # eg Narrow

        # write row
        # row = [volume, fileid, phase, craft, target, instrument, filter, note] # keep in sync with fields, above
        # print row # too slow
        # writer.writerow(row)

    filein.close()
    # fileout.close()
    

if __name__ == '__main__':
    initComposites()
    print 'done'
    

