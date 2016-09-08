
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

    #     # get number of files to process
    #     nfiles = len(os.listdir(importSubfolder))
    # else:
    #     nfiles = 1


    voydir = os.getcwd()
    os.chdir(importSubfolder)

    # add spice info (spiceinit)
    print "Adding SPICE geometry info (spiceinit)..."
    # voydir = os.getcwd()
    # os.chdir(importSubfolder)
    # cmd = "parallel spiceinit from={} web=yes ::: *.cub" # error on some imq's
    # parallel spiceinit from={} \
    #     TSPK=/home/bburns/Desktop/Voyager/kernels/spk/jup100.bsp \
    #     SPK=/home/bburns/Desktop/Voyager/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp \
    #     ::: *.cub
    # parallel spiceinit from={} \
        # TSPK=$VOYAGER/kernels/spk/jup100.bsp \
        # SPK=$VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp \
        # ::: *.cub
    # tspk = "../../../kernels/spk/jup100.bsp"
    # spk = "../../../kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
    # tspk = "$VOYAGER/kernels/spk/jup100.bsp"
    # spk = "$VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"

    tspk = voydir + "/kernels/spk/jup100.bsp"
    spk = voydir + "/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
    cmd = "parallel spiceinit from={} TSPK=%s SPK=%s ::: C???????.cub" % (tspk, spk)
    print cmd
    lib.system(cmd)
    print

    # now we have level 0 files


    # remove reseau marks
    print "Removing reseau marks (findrx, remrx)..."
    cmd = "parallel findrx from={} ::: C???????.cub"
    print cmd
    lib.system(cmd)
    #. fails unless write to diff file, but shouldn't
    # cmd = 'parallel remrx from={} to="" ::: *.cub'
    cmd = 'parallel remrx from={} to={.}rx.cub ::: C???????.cub'
    print cmd
    lib.system(cmd)
    print

    #. remove noise, hotpixels, etc

    # rotate 180
    print "Rotating 180 degrees..."
    # cmd = "parallel rotate from={} to={} degrees=180 interp=nearestneighbor ::: *.cub"
    # fails if write to same file
    # **I/O ERROR** Unable to open Table [InstrumentPointing] in file [C1462329.cub].
    # **I/O ERROR** Unable to read Table [InstrumentPointing].
    # **I/O ERROR** Error reading data from Table [InstrumentPointing].
    cmd = "parallel rotate from={} to={.}rot.cub degrees=180 interp=nearestneighbor ::: *rx.cub"
    print cmd
    lib.system(cmd)
    print

    # calibrate (voycal)
    print "Calibrating (voycal)..."
    # cmd = "parallel voycal from={} to={} ::: *.cub"
    cmd = "parallel voycal from={} to={.}cal.cub ::: *rxrot.cub"
    # fails if write to same file
    # **ERROR** Unable to initialize camera model from group [Instrument].
    # **I/O ERROR** Unable to open Table [SunPosition] in file [C1460413rot.cub].
    # **I/O ERROR** Unable to read Table [SunPosition].
    # **PROGRAMMER ERROR** Unable to find Table [SunPosition].
    print cmd
    lib.system(cmd)
    print


    # now we have level 1 files in *rxrotcal.cub



    #---

    # # open positions.csv file for target angular size info
    # csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # # read in brightness.csv file, which contains settings for problem images
    # brightnessInfo = lib.readCsv(config.dbBrightness)

    # # iterate through all available images
    # csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    # nfile = 1
    # for row in csvFiles:
    #     volume = row[config.colFilesVolume]
    #     fileId = row[config.colFilesFileId]
    #     filter = row[config.colFilesFilter]

    #     # if volume!=filterVolume: continue # filter on desired volume
    #     if volume!=filterVolume and fileId!=filterImageId: continue # filter on desired volume

    #     # get expected angular size (as fraction of frame) - joins on positions.csv file
    #     imageFraction = lib.getImageFraction(csvPositions, fileId)

    #     # get filenames
    #     infile = lib.getFilepath('convert', volume, fileId, filter)
    #     outfile = lib.getFilepath('adjust', volume, fileId, filter)
    #     print 'Volume %s adjusting %d/%d: %s     \r' % (volume,nfile,nfiles,infile),

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
    #     nfile += 1

    # fPositions.close()
    # fFiles.close()
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


