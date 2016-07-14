
# build centers<volnum>.csv file for a volume by attempting to center images in files.csv


import os
import os.path

import config
import lib
import libimg



def calcCenters(volumeNum):
    "calculate centers for images in the given volume and write to db/centers<volnum>.csv"
    
    volumeStr = str(volumeNum)
    
    #. image type to read will default to CALIB, but can override to use files from different subfolder
    imageType = 'Calib'
    
    # imagespath = lib.getImagespath(volumeNum)
    imagesfolder = config.imagesFolder + '/' + imageType + '/VGISS_' + str(volumeNum)
    
    # open the centers<vol>.csv file for writing
    filename = 'centers' + volumeStr + '.csv'
    fileout = open(filename, 'wb')
    fields = 'fileId,x,y'.split(',') # keep in synch with row, below
    writer = csv.writer(fileout)
    writer.writerow(fields)
    
    # open the files.csv file for reading
    filein = open(config.filesdb, 'rt')
    reader = csv.reader(filein)
    
    # iterate over all available files
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
            if volume==volumeStr:

                fileId = row[config.filesColFileId] # eg C1385455
                # phase = row[config.filesColPhase] # eg Jupiter
                # craft = row[config.filesColCraft] # eg Voyager1
                # target = row[config.filesColTarget] # eg Io
                # instrument = row[config.filesColInstrument] # eg Narrow
                # filter = row[config.filesColFilter] # eg Orange
                # note = row[config.filesColNote] 
                # print volume, fileId, phase, craft, target, instrument, filter
                # if debug: print 'row',row[:-1] # skip note

                infiletitle = fileId + '_' + imageType + '_' + filter + '.png'
                infilepath = imagesfolder + '/' + infiletitle
                print infilepath

                center = libimg.findCenter(infilepath)
                x,y = center
                x = -x
                y = -y

                row = [fileId,x,y]
                print row
                writer.writerow(row)

        i += 1

    filein.close()
    fileout.close()
    
    #.
    # blobThreshold = config.blobThreshold
    # fileid = filename.split('_')[0] # eg C1385455
    # blobThreshold = getBlobThreshold(fileid)
    # libimg.centerImageFile(infile, outfile, blobThreshold, config.rotateImage)
    # libimg.centerImageFile(infile, outfile, config.rotateImage, config.centerMethod, config.drawBoundingBox, config.drawCrosshairs)
    # libimg.centerImageFile(infile, outfile)


if __name__ == '__main__':
    os.chdir('..')
    calcCenters(5101)
    print 'done'
    
