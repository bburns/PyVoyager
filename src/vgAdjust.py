
"""
vg adjust command

Build adjusted images from plain png images (rotate 180, stretch histogram).
"""

import csv
import os
import os.path

import config
import lib
import libimg

import vgConvert


def vgAdjust(filterVolume='', filterImageId='', optionOverwrite=False, directCall=True, optionRaw=False):

    "Build adjusted images for given volume, if they don't exist yet"

    if optionRaw:
        print '--raw option is not yet implemented'
        return

    filterVolume = str(filterVolume) # eg '5101'

    if filterVolume!='':

        inputSubfolder = lib.getSubfolder('convert', filterVolume)
        outputSubfolder = lib.getSubfolder('adjust', filterVolume)

        # quit if volume folder exists
        if os.path.isdir(outputSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + outputSubfolder
            return

        # build the plain images for the volume, if not already there
        vgConvert.vgConvert(filterVolume, optionOverwrite=False, directCall=False)

        # make new folder
        lib.mkdir_p(outputSubfolder)

        # get number of files to process
        nfiles = len(os.listdir(inputSubfolder))
    else:
        nfiles = 1

    # open positions.csv file for target angular size info
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # read in brightness.csv file, which contains settings for problem images
    brightnessInfo = lib.readCsv(config.dbBrightness)

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for row in csvFiles:
        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]
        filter = row[config.colFilesFilter]

        # if volume!=filterVolume: continue # filter on desired volume
        if volume!=filterVolume and fileId!=filterImageId: continue # filter on desired volume

        # get expected angular size (as fraction of frame) - joins on positions.csv file
        imageFraction = lib.getImageFraction(csvPositions, fileId)

        # get filenames
        infile = lib.getFilepath('convert', volume, fileId, filter)
        outfile = lib.getFilepath('adjust', volume, fileId, filter)
        # print 'Volume %s adjusting %d/%d: %s     \r' % (volume,nfile,nfiles,infile),
        print 'Volume %s adjusting %d/%d: %s     ' % (volume,nfile,nfiles,infile)

        # get max brightness value to override noise/hot pixels in some images
        brightnessInfoRecord = brightnessInfo.get(fileId)
        if brightnessInfoRecord:
            maxvalue = int(brightnessInfoRecord['maxvalue'])
        else:
            maxvalue = None

        # only stretch the histogram if target is large enough (small moons get blown out)
        dontStretchHistogram = (imageFraction <= config.adjustHistogramImageFractionMinimum)
        if dontStretchHistogram:
            maxvalue = 255

        # adjust the image
        if os.path.isfile(infile):
            libimg.adjustImageFile(infile, outfile, maxvalue)
        else:
            print 'Warning: missing image file', infile
        nfile += 1

    fPositions.close()
    fFiles.close()
    print

if __name__ == '__main__':
    os.chdir('..')
    # vgAdjust(5101)
    # vgAdjust('','C1502309') # 5102 callisto small
    # vgAdjust('','C1553140') # 5106 callisto small
    # vgAdjust('','C1640140') # 5117 ganymede limb
    # vgAdjust('','C1642203') # 5117 callisto with big white area and noise
    # vgAdjust('','C1640344') # 5117 ganymede giant hotspot and noise - need brightness.csv
    print 'done'


