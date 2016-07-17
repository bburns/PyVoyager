
# build composites.csv, which will attempt to describe how to combine image channels
# based on time, filter, target, camera, NOTE field
# (right now just filter, target, camera fields)


# the best way to understand this algorithm is to look at some sample data and
# understand that it's grouping records together by looking for repeating patterns.
# or at the moment, just repeated filters for the same target/camera.
# eg
# from files.csv
# volume,fileid,phase,craft,target,time,instrument,filter,note
# 5101,C1471038,Jupiter,Voyager1,Jupiter,1979-01-09T00:48:40,Narrow,Uv
# 5101,C1471040,Jupiter,Voyager1,Jupiter,1979-01-09T00:51:49,Narrow,Blue
# 5101,C1471042,Jupiter,Voyager1,Jupiter,1979-01-09T00:55:01,Narrow,Green
# 5101,C1471044,Jupiter,Voyager1,Jupiter,1979-01-09T00:58:13,Narrow,Orange
# 5101,C1471307,Jupiter,Voyager1,Jupiter,1979-01-09T00:59:55,Narrow,Uv
# 5101,C1471309,Jupiter,Voyager1,Jupiter,1979-01-09T01:03:04,Narrow,Blue
# 5101,C1471311,Jupiter,Voyager1,Jupiter,1979-01-09T01:06:16,Narrow,Green
# 5101,C1471313,Jupiter,Voyager1,Jupiter,1979-01-09T01:45:54,Narrow,Orange
# =>
# composites.csv
# volume,compositeId,centerId,filter
# 5101,C1471038,C1471038,Uv
# 5101,C1471038,C1471040,Blue
# 5101,C1471038,C1471042,Green
# 5101,C1471038,C1471044,Orange
# 5101,C1471307,C1471307,Uv
# 5101,C1471307,C1471309,Blue
# 5101,C1471307,C1471311,Green
# 5101,C1471307,C1471313,Orange

# ie when it catches the repeated Uv filter, it writes out the intervening records as a group - a composite record.
# different targets and cameras can be interleaved because it keeps different circular buffers for each target/camera combination.

#.. also need to look at the time to make sure they're all within a certain range -
# eg the last orange filter is 40 mins after the last green one,
# so belongs in a different group


import os
import csv
import pprint

import config
import lib


#. in config -
#. max number of records in a group
# 7
#. max time delta between all records in a group
# tdeltamax = 7*5mins?

# debug = True
debug = False


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

    # this will store circular buffers with 7 empty lists - the maximum number of filters in a group we're checking for
    circbuffers = {}

    i = 0
    for row in reader:
        if row==[] or row[0][0]=="#": # skip blanks and comments
            continue
        if i==0: # get column headers
            fields = row
        else:
            # get field values
            # volume,fileid,phase,craft,target,time,instrument,filter,note
            volume = row[config.filesColVolume] # eg 5101
            fileid = row[config.filesColFileId] # eg C1385455
            phase = row[config.filesColPhase] # eg Jupiter
            craft = row[config.filesColCraft] # eg Voyager1
            target = row[config.filesColTarget] # eg Io
            instrument = row[config.filesColInstrument] # eg Narrow
            filter = row[config.filesColFilter] # eg Orange
            # note = row[config.filesColNote]
            # print volume, fileid, phase, craft, target, instrument, filter
            if debug: print 'row',row[:-1] # skip note

            # get correct circular buffer
            bufferKey = target+instrument # eg TritonNarrow
            if debug: print 'bufferkey', bufferKey
            buffer = circbuffers.get(bufferKey)
            if buffer==None:
                buffer = [[],[],[],[],[],[],[]]
                circbuffers[bufferKey] = buffer

            # now iterate over rows in circular buffer, checking for matches
            # if found a match, assume it indicates the end of a cycle, and that the intervening similar records are part of a group
            # so write them out together, and reset the buffer
            for bufferRow in reversed(buffer):
                if bufferRow==[]:
                    pass
                else:
                    if debug: print 'bufferrow',bufferRow[:-1]
                    # we know the target and instrument are the same, so can skip them
                    bufferVolume = bufferRow[config.filesColVolume] # eg 5101
                    bufferFileid = bufferRow[config.filesColFileId] # eg C1385455
                    bufferPhase = bufferRow[config.filesColPhase] # eg Jupiter
                    bufferCraft = bufferRow[config.filesColCraft] # eg Voyager1
                    bufferFilter = bufferRow[config.filesColFilter] # eg Orange
                    # bufferNote = bufferRow[config.filesColNote]
                    if filter==bufferFilter:
                        if debug: print 'filters match - check other values'
                        # if phase==bufferPhase and craft==bufferCraft and target==bufferTarget and instrument==bufferInstrument:
                        # if True:
                        if volume==bufferVolume: # actually had some cases of this failing
                            # print 'values match - assume we have a cycle, so dump non-empty buffer rows into composites.csv, clear buffer'
                            # print buffer
                            # pprint.pprint(buffer)
                            # print [row[config.filesColFilter] for row in buffer]
                            # print buffer.join('\n')
                            nonemptyRows = [rowx for rowx in buffer if rowx != []] # bug - had used 'row' for this variable, but it's not local! overwrote existing row variable
                            outCompositeId = None
                            for nonemptyRow in nonemptyRows:
                                # volume,compositeId,centerId,filter
                                outVolume = nonemptyRow[config.filesColVolume]
                                if outCompositeId == None:
                                    outCompositeId = nonemptyRow[config.filesColFileId]
                                outCenterId = nonemptyRow[config.filesColFileId]
                                outFilter = nonemptyRow[config.filesColFilter]
                                # if just a single row, write it out as a clear image so shows up as b&w
                                if len(nonemptyRows) == 1:
                                    outFilter = 'Clear'
                                outRow = [outVolume, outCompositeId, outCenterId, outFilter]
                                if debug: print 'outrow',outRow
                                writer.writerow(outRow)
                            buffer = [[],[],[],[],[],[],[]]
                            circbuffers[bufferKey] = buffer


            # add row to buffer
            buffer.pop(0) # remove from front of list
            buffer.append(row) # append item to end of list
            # buffer.append(row[:-1]) # append item to end of list
            # if debug: print buffer

        # write row
        # row = [volume, fileid, phase, craft, target, instrument, filter, note] # keep in sync with fields, above
        # print row # too slow
        # writer.writerow(row)
        i += 1
        # print

    filein.close()
    fileout.close()


if __name__ == '__main__':
    os.chdir('..')
    initComposites()
    print 'done'


