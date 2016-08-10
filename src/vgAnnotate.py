
"""
vg annotate command

Build annotated images from mosaics, composites, or centered images.
"""

import csv
import os
import os.path

import config
import lib
import libimg

import vgMosaic


#. change input from composite to mosaic


#. handle indiv images also
def vgAnnotate(filterVolume, optionOverwrite=False, directCall=True):
    
    "Build annotated images for given volume, if they don't exist yet"

    filterVolume = str(filterVolume) # eg '5101'
    # mosaicsSubfolder = config.mosaicsFolder + 'VGISS_' + filterVolume + '/'
    # compositesSubfolder = config.compositesFolder + 'VGISS_' + filterVolume + '/'
    # annotationsSubfolder = config.annotationsFolder + 'VGISS_' + filterVolume + '/'
    inputSubfolder = lib.getSubfolder('composite', filterVolume)
    outputSubfolder = lib.getSubfolder('annotate', filterVolume)

    # build the plain mosaic for the volume, if not already there
    if filterVolume!='':
        
        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall:
                print "Folder exists - skipping vg annotate step: " + outputSubfolder
            return

        # build the mosaics if not already there
        #. not yet
        # vgMosaic.vgMosaic(filterVolume, optionOverwrite=False, directCall=False)

        # make new folder
        lib.mkdir(outputSubfolder)

    # get number of files to process
    nfiles = len(os.listdir(inputSubfolder))

    # open positions.csv file for target distance
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)
    
    # iterate through all available files
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for row in csvFiles:
        volume = row[config.colFilesVolume]
        if volume!=filterVolume: continue # filter on desired volume

        fileId = row[config.colFilesFileId]
        # filter = row[config.colFilesFilter]
        # system = row[config.colFilesSystem]
        # craft = row[config.colFilesCraft]
        # target = row[config.colFilesTarget]
        # camera = row[config.colFilesCamera]
        
        time = row[config.colFilesTime].replace('T', ' ')
        note = row[config.colFilesNote].title()

        # annotate the file
        infile = lib.getFilepath('mosaic', volume, fileId)
        if not os.path.isfile(infile):
            infile = lib.getFilepath('composite', volume, fileId)
            
        outfile = lib.getFilepath('annotate', volume, fileId)
        
        if os.path.isfile(infile):
            
            # get distance
            rowPositions = lib.getJoinRow(csvPositions, config.colPositionsFileId, fileId)
            if rowPositions:
                distanceKm = int(rowPositions[config.colPositionsDistance])
                distanceKm = format(distanceKm, ',')
                distance = 'Distance: ' + distanceKm + ' km'
            else:
                distance = ''
            
            print 'Volume %s annotating %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
            # print 'Volume %s annotating %d/%d: %s     ' % (volume,nfile,nfiles,infile)
            # print fileId, time, distance
            libimg.annotateImageFile(infile, outfile, fileId, time, distance, note)
            nfile += 1

    fPositions.close()
    fFiles.close()
    print

if __name__ == '__main__':
    os.chdir('..')
    vgAnnotate(5101)
    print 'done'




