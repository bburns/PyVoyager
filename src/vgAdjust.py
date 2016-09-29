
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
import libisis

import vgImport


def vgAdjust(filterVolume='', filterImageId='', optionOverwrite=False, directCall=True):

    "Adjust image cubes for given volume or file"

    filterVolume = str(filterVolume) # eg '5101'

    if filterVolume:

        importSubfolder = lib.getSubfolder('import', filterVolume)

        # quit if volume folder exists
        if os.path.isdir(importSubfolder) and optionOverwrite==False:
            if directCall: print "Folder exists: " + importSubfolder
            return

        # import the volume, if not already there
        vgImport.vgImport(filterVolume, optionOverwrite=False, directCall=False)

        # get number of files to process
        nfiles = lib.getNfiles(importSubfolder)
    else:
        nfiles = 1


    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for row in csvFiles:

        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]
        filter = row[config.colFilesFilter]

        # filter on desired volume or file
        if volume!=filterVolume and fileId!=filterImageId: continue

        # get filenames
        cubefile = lib.getFilepath('import', volume, fileId)

        if not os.path.isfile(cubefile):
            print 'warning: missing file', cubefile
            continue

        # print 'Volume %s adjusting %d/%d: %s     \r' % (volume,nfile,nfiles,cubefile),
        print 'Volume %s adjusting %d/%d: %s     ' % (volume,nfile,nfiles,cubefile)

        # get history so can see what steps we've done before
        history = libisis.getHistory(cubefile)

        # find and remove reseau marks
        print "Removing reseau marks (findrx, remrx)..."
        if not 'findrx' in history:
            cmd = "findrx from=%s" % cubefile
            print cmd
            lib.system(cmd)
        if not 'remrx' in history:
            rxname = cubefile[:-4] + "rx.cub"
            cmd = "remrx from=%s to=%s" % (cubefile, rxname)
            print cmd
            lib.system(cmd)
            lib.replaceFile(cubefile, rxname)

        #. remove noise, hotpixels, etc

        # # rotate 180
        # #. don't need this, as cam2map does it automatically
        # #. but would be nice to flip when export jpegs for browsing etc
        # print "Rotating 180 degrees..."
        # if not 'rotate' in history:
        #     rotname = cubefile[:-4] + 'rot.cub'
        #     cmd = "rotate from=%s to=%s degrees=180 interp=nearestneighbor" % (cubefile, rotname)
        #     print cmd
        #     lib.system(cmd)
        #     lib.replaceFile(cubefile, rotname)

        # #. this is segfaulting on C1465339 and killing virtualbox - why?
        # #. plus it triples the filespace needed, as stores as floating points,
        # #  for little gain (?), so maybe skip this?
        # #. does this step do the flatfield correction? could we do it better ourselves?
        # # calibrate (voycal)
        # print "Calibrating (voycal)..."
        # if not 'voycal' in history:
        #     calname = cubefile[:-4] + 'cal.cub'
        #     cmd = "voycal from=%s to=%s" % (cubefile, calname)
        #     print cmd
        #     lib.system(cmd)
        #     lib.replaceFile(cubefile, calname)

        print

        # now we have level 1 files in *.cub

        nfile += 1

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


