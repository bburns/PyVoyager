
"""
vg adjust command

Adjust image cubes (calibrate, rotate 180, dereseau, ...)
"""

import csv
import os
import os.path

import config
import lib
import libimg

import vgImport


def vgAdjust(filterVolume='', filterImageId='', optionOverwrite=False, directCall=True):

    "Build adjusted images for given volume, if they don't exist yet"

    filterVolume = str(filterVolume) # eg '5101'

    if filterVolume!='':

        importSubfolder = lib.getSubfolder('import', filterVolume)

        # quit if volume folder exists
        if os.path.isdir(importSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + importSubfolder
            return

        # import the volume, if not already there
        vgImport.vgImport(filterVolume, optionOverwrite=False, directCall=False)

        # make new folder
        lib.mkdir(importSubfolder)

        # get number of files to process
        #. ignore any folders incl . and ..
        nfiles = len(os.listdir(importSubfolder))
    else:
        nfiles = 1


    # os.chdir(importSubfolder)

    # # remove reseau marks
    # print "Removing reseau marks (findrx, remrx)..."
    # cmd = "parallel findrx from={} ::: C???????.cub"
    # print cmd
    # lib.system(cmd)
    # #. fails unless write to a different file, but shouldn't
    # # cmd = 'parallel remrx from={} to="" ::: *.cub'
    # cmd = 'parallel remrx from={} to={.}rx.cub ::: C???????.cub'
    # # cmd = 'parallel remrx from={} to={.}rx.cub && rm {} && mv {.}rx.cub {} ::: C???????.cub'
    # print cmd
    # lib.system(cmd)
    # print

    # #. remove noise, hotpixels, etc

    # # rotate 180
    # print "Rotating 180 degrees..."
    # # cmd = "parallel rotate from={} to={} degrees=180 interp=nearestneighbor ::: *.cub"
    # # fails if write to same file
    # # **I/O ERROR** Unable to open Table [InstrumentPointing] in file [C1462329.cub].
    # # **I/O ERROR** Unable to read Table [InstrumentPointing].
    # # **I/O ERROR** Error reading data from Table [InstrumentPointing].
    # cmd = "parallel rotate from={} to={.}rot.cub degrees=180 interp=nearestneighbor ::: *rx.cub"
    # print cmd
    # lib.system(cmd)
    # print

    # # calibrate (voycal)
    # print "Calibrating (voycal)..."
    # # cmd = "parallel voycal from={} to={} ::: *.cub"
    # cmd = "parallel voycal from={} to={.}cal.cub ::: *rxrot.cub"
    # # fails if write to same file
    # # **ERROR** Unable to initialize camera model from group [Instrument].
    # # **I/O ERROR** Unable to open Table [SunPosition] in file [C1460413rot.cub].
    # # **I/O ERROR** Unable to read Table [SunPosition].
    # # **PROGRAMMER ERROR** Unable to find Table [SunPosition].
    # print cmd
    # lib.system(cmd)
    # print

    #---

    # # open positions.csv file for target angular size info
    # csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # # read in brightness.csv file, which contains settings for problem images
    # brightnessInfo = lib.readCsv(config.dbBrightness)

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for row in csvFiles:
        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]
        filter = row[config.colFilesFilter]

        # if volume!=filterVolume: continue # filter on desired volume
        if volume!=filterVolume and fileId!=filterImageId: continue # filter on desired volume

        # get filenames
        filename = lib.getFilepath('import', volume, fileId)

        if not os.path.isfile(filename):
            #.
            # print 'warning: missing file', filename
            continue

        # print 'Volume %s adjusting %d/%d: %s     \r' % (volume,nfile,nfiles,filename),
        print 'Volume %s adjusting %d/%d: %s     ' % (volume,nfile,nfiles,filename)


        #. get history so can see what steps we've done before
        # history =


        # remove reseau marks
        print "Removing reseau marks (findrx, remrx)..."
        cmd = "findrx from=%s" % filename
        print cmd
        lib.system(cmd)
        rxname = filename[:-4] + "rx.cub"
        cmd = "remrx from=%s to=%s && rm %s && mv %s %s" % \
              (filename, rxname, filename, rxname, filename)
        print cmd
        lib.system(cmd)

        #. remove noise, hotpixels, etc

        # don't need this, as cam2map does it automatically
        # # rotate 180
        # print "Rotating 180 degrees..."
        # rotname = filename[:-4] + 'rot.cub'
        # cmd = "rotate from=%s to=%s degrees=180 interp=nearestneighbor && rm %s && mv %s %s" % \
        #       (filename, rotname, filename, rotname, filename)
        # print cmd
        # lib.system(cmd)

        #. this is segfaulting on C1465339 and killing virtualbox - why?
        # # calibrate (voycal)
        # print "Calibrating (voycal)..."
        # calname = filename[:-4] + 'cal.cub'
        # cmd = "voycal from=%s to=%s && rm %s && mv %s %s" % \
        #       (filename, calname, filename, calname, filename)
        # print cmd
        # lib.system(cmd)



        print


    #     # get expected angular size (as fraction of frame) - joins on positions.csv file
    #     imageFraction = lib.getImageFraction(csvPositions, fileId)

    #     # get max brightness value to override noise/hot pixels in some images
    #     # maxvalue = lib.getMaxValue(csvBrightness, fileId) # will be None if no record avail
    #     brightnessInfoRecord = brightnessInfo.get(fileId)
    #     if brightnessInfoRecord:
    #         maxvalue = int(brightnessInfoRecord['maxvalue'])
    #     else:
    #         maxvalue = None

    #     # only stretch the histogram if target is large enough (small moons get blown out)
    #     # doStretchHistogram = (imageFraction > config.adjustHistogramImageFractionMinimum)
    #     dontStretchHistogram = (imageFraction <= config.adjustHistogramImageFractionMinimum)
    #     if dontStretchHistogram:
    #         maxvalue = 255

    #     # adjust the image
    #     if os.path.isfile(infile):
    #         # libimg.adjustImageFile(infile, outfile, doStretchHistogram)
    #         libimg.adjustImageFile(infile, outfile, maxvalue)
    #     else:
    #         print 'Warning: missing image file', infile



        # now we have level 1 files in *rxrotcal.cub


        nfile += 1

    # fPositions.close()
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


