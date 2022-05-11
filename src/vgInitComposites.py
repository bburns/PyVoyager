
"""
vg init composites command

Build composites.csv, which will attempt to describe how to combine image channels
based on system, craft, target, camera, time, filter.

The best way to understand this algorithm is to look at some sample data and
understand that it's grouping records together by looking for repeating patterns.

#.(or at the moment, just repeated filters for the same system/craft/target/camera -
could extend it to try to look for more specific repeating patterns,
but it seems to work fairly well like this)

eg
from files.csv
volume,fileid,phase,craft,target,time,instrument,filter,note
5101,C1471038,Jupiter,Voyager1,Jupiter,1979-01-09T00:48:40,Narrow,Uv
5101,C1471040,Jupiter,Voyager1,Jupiter,1979-01-09T00:51:49,Narrow,Blue
5101,C1471042,Jupiter,Voyager1,Jupiter,1979-01-09T00:55:01,Narrow,Green
5101,C1471044,Jupiter,Voyager1,Jupiter,1979-01-09T00:58:13,Narrow,Orange
5101,C1471307,Jupiter,Voyager1,Jupiter,1979-01-09T00:59:55,Narrow,Uv
5101,C1471309,Jupiter,Voyager1,Jupiter,1979-01-09T01:03:04,Narrow,Blue
5101,C1471311,Jupiter,Voyager1,Jupiter,1979-01-09T01:06:16,Narrow,Green
5101,C1471313,Jupiter,Voyager1,Jupiter,1979-01-09T01:45:54,Narrow,Orange < note time delta ~40mins

you want to make some records like this -
composites.csv
volume,compositeId,centerId,filter
5101,C1471038,C1471038,Uv
5101,C1471038,C1471040,Blue
5101,C1471038,C1471042,Green
5101,C1471038,C1471044,Orange
5101,C1471307,C1471307,Uv
5101,C1471307,C1471309,Blue
5101,C1471307,C1471311,Green
5101,C1471313,C1471313,Orange

ie when it catches the repeated Uv filter, it writes out the intervening records as a group -
a composite record.

Different targets and cameras are sometimes interleaved in files.csv,
but it can disentangle them because it keeps different circular buffers
for each target/camera combination.
"""

import os
import csv
import pprint

import config
import lib


#. put in config -
# max number of channels in a composite image
maxRecordsInGroup = 7

# max time delta between channels in a composite image
tdeltamax = 6*60 # secs, eg 6 mins at neptune


# debug = True
debug = False



def newBuffer():
    "return a new circular buffer, eg [[],[],[],[],[],[],[]]"
    buffer = []
    for i in range(maxRecordsInGroup):
        buffer.append([])
    return buffer


def dumpBufferAsGroup(csvComposites, buffer):
    "dump buffer records as a group to csvComposites file"
    # get nonempty rows
    rows = [row for row in buffer if row != []]
    outCompositeId = None
    for row in rows:
        # need volume,compositeId,centerId,filter
        if outCompositeId is None:
            outCompositeId = row[config.colFilesFileId]
        outFileId = row[config.colFilesFileId]
        outVolume = row[config.colFilesVolume]
        outFilter = row[config.colFilesFilter]
        outRow = [outCompositeId, outFileId, outVolume, outFilter]
        if debug: print 'outrow',outRow
        csvComposites.writerow(outRow)


def vgInitComposites():
    "Build the composites.csv file from likely looking groups of images in files.csv"

    # open the composites.csv file for writing
    csvComposites, fComposites = lib.openCsvWriter(config.dbComposites)
    # fields = 'compositeId,imageId,volume,filter'.split(',') # keep in synch with row, below
    # csvComposites.writerow(fields) # don't write till after sorted

    # this will store circular buffers with 7 empty lists -
    # the maximum number of filters in a group we're checking for
    circbuffers = {}

    # iterate over all image files
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    for row in csvFiles:

        # get field values
        # volume,fileId,phase,craft,target,time,instrument,filter,note
        fileId = row[config.colFilesFileId] # eg C1385455
        volume = row[config.colFilesVolume] # eg 5101
        system = row[config.colFilesSystem] # eg Jupiter
        craft = row[config.colFilesCraft] # eg Voyager1
        target = row[config.colFilesTarget] # eg Io
        time = row[config.colFilesTime] # eg 1986-01-18T15:35:10
        camera = row[config.colFilesCamera] # eg Narrow
        filter = row[config.colFilesFilter] # eg Orange
        # note = row[config.colFilesNote]
        if debug: print 'row',row[:-1] # skip note

        # if time[0]!='U': # some are UNKNOWN or UNK
        try:
            nsecs1970 = lib.secondsSince1970(time)
        except:
            # print 'badtime',time
            nsecs1970 = 0
        row.append(nsecs1970) # stick it on the end

        # get correct circular buffer
        bufferKey = system + craft + target + camera # eg JupiterVoyager1TritonNarrow
        if debug: print 'bufferkey', bufferKey
        buffer = circbuffers.get(bufferKey)
        if buffer is None:
            # buffer = [[],[],[],[],[],[],[]]
            buffer = newBuffer()
            circbuffers[bufferKey] = buffer

        # if tdelta between this and last record in the buffer > threshold,
        # dump the contents of the buffer as a group, reset it to empty
        lastBufferRow = buffer[-1]
        if lastBufferRow != []:
            # lastTime = lastBufferRow[config.colFilesTime] # eg 1986-01-18T15:35:10
            # lastNsecs1970 = lib.secondsSince1970(lastTime)
            lastNsecs1970 = lastBufferRow[-1] # stuck onto the end
            if (nsecs1970 - lastNsecs1970) > tdeltamax: #.param eg 6min at neptune
                # print 'tdelta>th - dump current buffer as group'
                # for r in buffer:
                    # print r
                # print row
                dumpBufferAsGroup(csvComposites, buffer)
                buffer = newBuffer()
                circbuffers[bufferKey] = buffer

        # now iterate over rows in circular buffer, checking for matches
        # if found a match, ASSUME it indicates the end of a cycle,
        # and that the intervening similar records are part of a group.
        # so write them out together, and reset the buffer.
        for bufferRow in reversed(buffer):
            if bufferRow==[]: continue # skip empty buffer rows
            if debug: print 'bufferrow',bufferRow[:-1]
            # we know the system, craft, target and camera are the same, so can skip them
            # bufferVolume = bufferRow[config.colFilesVolume] # eg 5101
            # bufferFileId = bufferRow[config.colFilesFileId] # eg C1385455
            # bufferSystem = bufferRow[config.colFilesSystem] # eg Jupiter
            # bufferCraft = bufferRow[config.colFilesCraft] # eg Voyager1
            # bufferTime = bufferRow[config.colFilesTime] # eg 1986-01-18T15:35:10
            # bufferNote = bufferRow[config.colFilesNote]
            bufferFilter = bufferRow[config.colFilesFilter] # eg Orange
            if filter==bufferFilter:
                if debug: print 'filters match - assume we have a cycle - dump buffer as group'
                dumpBufferAsGroup(csvComposites, buffer)
                buffer = newBuffer()
                circbuffers[bufferKey] = buffer

        # now add current row to this buffer
        buffer.pop(0) # remove from front of list
        buffer.append(row) # append item to end of list

    # write any leftover buffer rows
    for key in circbuffers:
        buffer = circbuffers[key]
        dumpBufferAsGroup(csvComposites, buffer)

    fFiles.close()
    fComposites.close()

    # now sort the composites.csv file
    # (needs to be sorted so can be joined against other files,
    # and the leftover buffer rows will be all out of sorts)

    os.chdir('db')
    cmd = "sort %s /o %s" % ("composites.csv", "composites_temp.csv")
    os.system(cmd)

    fields = 'compositeId,imageId,volume,filter'
    fComposites = open("composites.csv", 'wb')
    fComposites.write(fields + '\n')
    fComposites.close()

    cmd = "cat %s >> %s" % ("composites_temp.csv", "composites.csv")
    os.system(cmd)

    # os.remove("composites_temp.csv")

    os.chdir('..')

    # need to keep the header row
    # csvComposites.writerow(fields) # don't write till after sorted



if __name__ == '__main__':
    os.chdir('..')
    vgInitComposites()
    print 'done'


