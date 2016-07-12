
# build composites.csv, which will attempt to describe how to combine image channels

# based on image number (~time), filter, target, camera, NOTE field


import os
import csv
import pprint

import config
import lib

        


# from files.csv
# volume,fileid,phase,craft,target,time,instrument,filter,note
# VGISS_5101,C1471038,Jupiter,Voyager1,Jupiter,1979-01-09T00:48:40,Narrow,UV,ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA
# VGISS_5101,C1471040,Jupiter,Voyager1,Jupiter,1979-01-09T00:51:49,Narrow,BLUE,ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA
# VGISS_5101,C1471042,Jupiter,Voyager1,Jupiter,1979-01-09T00:55:01,Narrow,GREEN,ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA
# VGISS_5101,C1471044,Jupiter,Voyager1,Jupiter,1979-01-09T00:58:13,Narrow,ORANGE,ROUTINE MULTISPECTRAL LONGITUDE COVERAGE; 1 OF 4 NA
# ->
# composites.csv
# volume,compositeId,centerId,filter
# VGISS_5101,C1471038,C1471038,UV
# VGISS_5101,C1471038,C1471040,BLUE
# VGISS_5101,C1471038,C1471042,GREEN
# VGISS_5101,C1471038,C1471044,ORANGE


# tdeltamax = 5mins

def initComposites():
    "build the composites.csv file from likely looking images in files.csv"
    
    # open the composites.csv file
    fileout = open(config.compositesdb, 'wb')
    fields = 'volume,compositeId,centerId,filter'.split(',') # keep in synch with row, below
    writer = csv.writer(fileout)
    writer.writerow(fields)
    
    # iterate over all image files
    filein = open(config.filesdb, 'rt')
    reader = csv.reader(filein)
    
    # circular buffer with 7 empty lists - the maximum number of filters in a group we're checking for
    #. but would need more to handle interpolated records for different cameras, targets etc
    buffer = [[],[],[],[],[],[],[]] 
    i = 0
    
    for row in reader:
        if row==[] or row[0][0]=="#":
            continue
        if i==0:
            fields = row
        else:
            # get field values
            # volume,fileid,phase,craft,target,time,instrument,filter,note
            volume = row[config.filesColVolume] # eg VGISS_5101
            fileid = row[config.filesColFileId] # eg C1385455
            phase = row[config.filesColPhase] # eg Jupiter
            craft = row[config.filesColCraft] # eg Voyager1
            target = row[config.filesColTarget] # eg Io
            instrument = row[config.filesColInstrument] # eg Narrow
            # filter = row[config.filesColFilter] # eg ORANGE
            filter = row[config.filesColFilter].title() # eg Orange
            note = row[config.filesColNote] 
            # print volume, fileid, phase, craft, target, instrument, filter
            # print row[:-1]

            # now iterate over circular buffer, checking for matches (skip last item in buffer though to avoid single cycle groups)
            # if found, assume it indicates the end of a cycle, and that the intervening similar records are part of a group
            # so write them out together, and reset the buffer
            # for bufferRow in reversed(buffer):
            for bufferRow in reversed(buffer[:-1]):
                if bufferRow==[]:
                    pass
                else:
                    bufferVolume = bufferRow[config.filesColVolume] # eg VGISS_5101
                    bufferFileid = bufferRow[config.filesColFileId] # eg C1385455
                    bufferPhase = bufferRow[config.filesColPhase] # eg Jupiter
                    bufferCraft = bufferRow[config.filesColCraft] # eg Voyager1
                    bufferTarget = bufferRow[config.filesColTarget] # eg Io
                    bufferInstrument = bufferRow[config.filesColInstrument] # eg Narrow
                    # bufferFilter = bufferRow[config.filesColFilter] # eg Orange
                    bufferFilter = bufferRow[config.filesColFilter].title() # eg Orange
                    # bufferNote = bufferRow[config.filesColNote] 
                    # print bufferRow[:-1] # skip note
                    # print bufferRow # skip note
                    if filter==bufferFilter:
                        # print 'filters match - check other values'
                        if phase==bufferPhase and craft==bufferCraft and target==bufferTarget and instrument==bufferInstrument:
                            # print 'values match - assume we have a cycle, so dump non-empty buffer rows into composites.csv, clear buffer'
                            # print buffer
                            # pprint.pprint(buffer)
                            # print [row[config.filesColFilter] for row in buffer]
                            # print buffer.join('\n')
                            outCompositeId = None
                            for bufferRow2 in buffer:
                                if bufferRow2==[]:
                                    pass
                                else:
                                    # volume,compositeId,centerId,filter
                                    outVolume = bufferRow2[config.filesColVolume]
                                    if outCompositeId == None:
                                        outCompositeId = bufferRow2[config.filesColFileId]
                                    outCenterId = bufferRow2[config.filesColFileId]
                                    outFilter = bufferRow2[config.filesColFilter].title()
                                    outRow = [outVolume, outCompositeId, outCenterId, outFilter]
                                    # print outRow
                                    writer.writerow(outRow)
                            buffer = [[],[],[],[],[],[],[]] 
                            
        
            # add row to buffer
            buffer.pop(0) # remove from front of list
            # buffer.append(row) # append item to end of list
            buffer.append(row[:-1]) # append item to end of list
            # print buffer

        # write row
        # row = [volume, fileid, phase, craft, target, instrument, filter, note] # keep in sync with fields, above
        # print row # too slow
        # writer.writerow(row)
        i += 1

    filein.close()
    fileout.close()
    

if __name__ == '__main__':
    os.chdir('..')
    initComposites()
    print 'done'
    

