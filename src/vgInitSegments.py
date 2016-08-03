
"""
vg init segments command

initialize db/segments.csv
"""


import os
import csv

import config
import lib


# hide some of the details of iterating down a single instrument type in files.csv and
# joining with positions.csv
# def filesdbOpenJoinPositions(camera):
#     ""
#     return {}
# def filesdbNext(fdb):
#     ""
#     pass
# def filesdbClose(fdb):
#     ""
#     pass


def vgInitSegments():
    "initialize segments.csv from files.csv and positions.csv"

    # # open segments.csv for writing
    # fileout = open(config.segmentsdb, 'wb')
    # # IMPORTANT: keep fields in synch with row, below, and config.segmentsCol*
    # fields = 'segmentId,fileIds,imageSource,nframes'.split(',')
    # writer = csv.writer(fileout)
    # writer.writerow(fields)
    # fileout.close()

    # # open files.csv for reading
    # fNarrow = open(config.filesdb, 'rt') # narrowrrow angle
    # fWide = open(config.filesdb, 'rt') # wide angle
    # readerNarrow = csv.reader(fNarrow)
    # readerWide = csv.reader(fWide)
    # row = readerNarrow.next() # read fields row
    # row = readerWide.next() # read fields row
    # # volume,fileid,phase,craft,target,time,instrument,filter,note
    # camera = ''
    # while camera!='Narrow':
    #     row = readerNarrow.next()
    #     camera = row[config.filesColInstrument]
    # print row
    # fWide.close()
    # fNarrow.close()

    # #. using a class might make this easier
    # fdb1 = filesdbOpenJoinPositions('Narrow')
    # fdb2 = filesdbOpenJoinPositions('Wide')
    # row1 = filesdbNext(fdb1)
    # row2 = filesdbNext(fdb2)
    # imageSize1 = row1[config.filesPositionsColImageSize]
    # imageSize2 = row2[config.filesPositionsColImageSize]

    # if imageSize2 < imageSize1:
    #     # write out row
    #     system = row2[config.filesColSystem]
    #     craft = row2[config.filesColCraft]
    #     target = row2[config.filesColTarget]
    #     # segmentId,fileIds,imageSource,nframes
    #     segmentId = system + '-' + craft + '-' + target
    #     fileId = row2[config.filesColFileId]
    #     imageSource =
    #     row = []
    # filesdbClose(fdb2)
    # filesdbClose(fdb1)

    # fdb1 = new Filesdb('Narrow')
    # fdb2 = new Filesdb('Wide')
    # row1 = fdb1.next()
    # row2 = fdb2.next()
    # imageSize1 = row1[config.filesPositionsColImageSize]
    # imageSize2 = row2[config.filesPositionsColImageSize]
    # fdb2.close()
    # fdb1.close()


if __name__ == '__main__':
    os.chdir('..')
    vgInitSegments()
    print 'done'






