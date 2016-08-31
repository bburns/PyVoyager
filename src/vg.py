
# vg
# voyager command line interface

"""
PyVoyager commands

  vg download            - download volume(s)
  vg unzip               - unzip volume(s)
  vg convert             - convert IMGs to PNGs
  vg adjust              - adjust images (rotate and enhance)
  vg denoise             - remove noise from images
  vg center              - center images
  vg inpaint             - fill in missing pixels where possible
  vg composite           - create color images
  vg map                 - build up 2d color maps
  vg colorize            - colorize images using 2d color maps
  vg crop                - crop/zoom in on images
  vg target              - copy images into target subfolders
  vg clips               - create bw or color clips
  vg movies              - create movies from clips
  vg list                - show status of local datasets
  vg clear <step> <vols> - remove volume folders

  vg test denoise        - run denoising tests
  vg test center         - run centering tests
  vg test composite      - run compositing tests

where most commands can be followed by <filter> and <options>, where

  <filter>     = [<volnums>] [<imageIds>] [<targetpath>]
                 (all are anded together)
  <volnums>    = 5101..5120 Voyager 1 Jupiter
                 6101..6121 Voyager 1 Saturn
                 5201..5214 Voyager 2 Jupiter
                 6201..6215 Voyager 2 Saturn
                 7201..7207 Voyager 2 Uranus
                 8201..8210 Voyager 2 Neptune
                 (ranges and wildcards like 5101-5104 or 51* are ok)
  <imageIds>   = imageId or range, like C1234567, C1234567-C1234569
  <targetpath> = [<system>]/[<spacecraft>]/[<target>]/[<camera>]
  <system>     = Jupiter|Saturn|Uranus|Neptune
  <spacecraft> = Voyager1|Voyager2
  <target>     = Jupiter|Io|Europa|, etc.
  <camera>     = Narrow|Wide
  <options>    = -y overwrite existing volume data

e.g. vg clips 8205 //triton
"""

import sys
import os
import inspect
import tabulate
import re


import config
import lib
import log

import vgDownload
import vgUnzip
import vgConvert
import vgAdjust
import vgDenoise
import vgCenter
import vgInpaint
import vgComposite
import vgMosaic
import vgMap
import vgCrop
import vgAnnotate
import vgTarget
import vgTitle
import vgClips
import vgPlot
import vgPages
import vgMovies

import vgList
import vgClear
import vgTestDenoise
import vgTestCenter
import vgTestComposite
import vgGrab
import vgInitFiles
import vgInitCenters
import vgInitComposites
import vgInitPositions
import vgInitErrata
import vgRetarget
import vgUncenter


# get command and arguments
args = sys.argv[1:] # remove command 'vg'
nargs = len(args)
if nargs==0:
    cmd = "help"
else:
    cmd = args.pop(0) # first item

# pick out and remove options from argument list
optionOverwrite = False
optionKeepLinks = False
optionAlign = False
optionList = [arg for arg in args if arg[0]=='-']
args = [arg for arg in args if arg[0]!='-']
for option in optionList:
    if option=='-y':
        optionOverwrite = True
    elif option=='-align':
        optionAlign = True
    elif option=='-keeplinks':
        optionKeepLinks = True
    else:
        print 'Error: unknown option',option
        print
        stop

# parse remaining <filter> arguments
filterVolumes = None
filterImageIds = None
filterTargetPath = None
for arg in args:
    if arg[0] in '0123456789':
        filterVolumes = lib.getVolumeNumbers(arg)
    elif arg[0].lower()=='c':
        filterImageIds = lib.getImageIds(arg)
    else:
        filterTargetPath = arg

# handle commands
if cmd=="download":
    for filterVolume in filterVolumes:
        vgDownload.vgDownload(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="unzip":
    for filterVolume in filterVolumes:
        vgUnzip.vgUnzip(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="convert":
    for filterVolume in filterVolumes:
        vgConvert.vgConvert(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="adjust":
    # for filterVolume in filterVolumes:
        # vgAdjust.vgAdjust(filterVolume, optionOverwrite)
    if filterImageIds:
        for imageId in filterImageIds:
            vgAdjust.vgAdjust('', imageId, optionOverwrite=True)
    else:
        for filterVolume in filterVolumes:
            vgAdjust.vgAdjust(filterVolume, '', optionOverwrite)
    lib.beep()

elif cmd=="denoise":
    for filterVolume in filterVolumes:
        vgDenoise.vgDenoise(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="center":
    log.start()
    if filterImageIds:
        for imageId in filterImageIds:
            vgCenter.vgCenter('', imageId, optionOverwrite)
    else:
        for filterVolume in filterVolumes:
            vgCenter.vgCenter(filterVolume, '', optionOverwrite)
    log.stop()
    lib.beep()

elif cmd=="inpaint":
    log.start()
    if filterImageIds:
        for imageId in filterImageIds:
            vgInpaint.vgInpaint('', imageId, optionOverwrite)
    else:
        for filterVolume in filterVolumes:
            vgInpaint.vgInpaint(filterVolume, '', optionOverwrite)
    log.stop()
    lib.beep()

elif cmd=="composite":
    # can filter on volumes and targetpath OR ids and targetpath, but not vols and ids
    if filterImageIds:
        for compositeId in filterImageIds:
            vgComposite.vgComposite(None, compositeId, filterTargetPath,
                                    optionOverwrite=True, optionAlign=optionAlign)
            # vgComposite.vgComposite(None, compositeId, None,
            # vgComposite.vgComposite(filterCompositeId=compositeId,
                                    # optionOverwrite=True, optionAlign=optionAlign)
    elif filterVolumes:
        for filterVolume in filterVolumes:
            vgComposite.vgComposite(filterVolume, None, filterTargetPath,
                                    optionOverwrite, optionAlign=optionAlign)
            # vgComposite.vgComposite(filterVolume, None, None,
            # vgComposite.vgComposite(filterVolume=filterVolume, None, None,
    # elif filterTargetPath:
    #     # vgComposite.vgComposite(None, None, filterTargetPath, optionAlign=optionAlign)
    #     vgComposite.vgComposite(filterTargetPath=filterTargetPath, optionAlign=optionAlign)
    lib.beep()

elif cmd=="mosaic":
    if filterVolumes is None:
        filterVolumes = volumes
    for filterVolume in filterVolumes:
        vgMosaic.vgMosaic(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="map":
    vgMap.vgMap(filterVolumes, optionOverwrite)
    lib.beep()

elif cmd=="crop":
    vgCrop.vgCrop(filterVolumes)
    lib.beep()

elif cmd=="annotate":
    for filterVolume in filterVolumes:
        vgAnnotate.vgAnnotate(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="target":
    # can filter on volumes and targetpath OR ids and targetpath, but not vols and ids
    #. check this logic - make like vg composite?
    if filterImageIds:
        for imageId in filterImageIds:
            vgTarget.vgTarget(None, imageId, filterTargetPath)
    elif filterVolumes:
        for filterVolume in filterVolumes:
            # vgTarget.vgTarget(filterVolume, '')
            vgTarget.vgTarget(filterVolume, '', filterTargetPath)
    else:
        # vgTarget.vgTarget('', filterTargetPath)
        vgTarget.vgTarget('', '', filterTargetPath)
    lib.beep()

elif cmd=="title":
    vgTitle.vgTitle(filterTargetPath)
    lib.beep()

elif cmd=="clips":
    # if filterVolumes is None:
        # filterVolumes = config.volumes
    vgClips.vgClips(filterVolumes, filterTargetPath, optionKeepLinks)
    lib.beep()

elif cmd=="plot":
    vgPlot.vgPlot()
    lib.beep()

elif cmd=="pages":
    vgPages.vgPages()
    lib.beep()

elif cmd=="movies":
    # vgMovies.vgMovies()
    vgMovies.vgMovies(filterVolumes, filterTargetPath, optionKeepLinks)
    lib.beep()

elif cmd=="list":
    vgList.vgList(filterVolumes)

elif cmd=="test":
    subject = args[0]
    if subject=='denoise':
        vgTestDenoise.vgTestDenoise()
    elif subject=='center':
        vgTestCenter.vgTestCenter()
    elif subject=='composite':
        vgTestComposite.vgTestComposite()

elif cmd=="grab":
    vgGrab.vgGrab()

# elif cmd=="uncenter":
#     for filterVolume in filterVolumes:
#         vgUncenter.vgUncenter(filterVolume)
#     lib.beep()

elif cmd=="retarget":
    oldTarget = args[0]
    newTarget = args[1]
    vgRetarget.vgRetarget(oldTarget, newTarget)

elif cmd=="clear":
    step = args[0] # eg 'adjust'
    if filterVolumes is None:
        print 'Specify volume(s) to clear'
    else:
        for filterVolume in filterVolumes:
            vgClear.vgClear(step, filterVolume)

elif cmd=="init":
    log.start()
    subject = args[0]
    if subject=='files':
        vgInitFiles.vgInitFiles()
    # elif subject=='centers':
    #     vols = args.pop(0)
    #     filterVolumes = lib.getVolumeNumbers(vols)
    #     for filterVolume in filterVolumes:
    #         vgInitCenters.vgInitCenters(filterVolume, optionOverwrite)
    elif subject=='composites':
        vgInitComposites.vgInitComposites()
    elif subject=='positions':
        vgInitPositions.vgInitPositions()
    elif subject=='errata':
        vgInitErrata.vgInitErrata()
    log.stop()
    lib.beep()

elif cmd=="help":
    pass
else:
    print
    print "Command not recognized."
    cmd = 'help'

if cmd=="help":
    print __doc__
