
# vg
# voyager command line interface

"""
PyVoyager commands

  vg download       - download volume(s)
  vg unzip          - unzip volume(s)
  vg convert        - convert IMGs to PNGs
  vg adjust         - adjust images (rotate and enhance)
  vg denoise        - remove noise from images
  vg center         - center images
  vg composite      - create color images
  vg target         - copy images into target subfolders
  vg clips          - create bw or color clips
  vg movies         - create movies from clips
  vg list           - show status of local datasets

  vg test center    - run centering tests
  vg test denoise   - run denoising tests

where most commands can be followed by <filter>, where

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

e.g. vg clips 8205 //triton

You can also add `-y` to a command to have it overwrite any existing data.
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
import vgComposite
import vgMosaic
import vgTarget
import vgClips
import vgSegments
import vgMovies
import vgList
import vgTestCenter
import vgTestDenoise
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


# pick out options from argument list
optionOverwrite = False
# optionBw = False
# optionColor = False
optionKeepLinks = False
options = [arg for arg in args if arg[0]=='-']
args = [arg for arg in args if arg[0]!='-']
for option in options:
    if option=='-y':
        optionOverwrite = True
    # elif option=='-bw':
        # optionBw = True
    # elif option=='-color':
        # optionColor = True
    elif option=='-keeplinks':
        optionKeepLinks = True


# parse remaining <filter> arguments


volnums = None
# volnums = config.volumes
# imageIds = []
imageIds = None
targetPath = None
for arg in args:
    if arg[0] in '0123456789':
        volnums = lib.getVolumeNumbers(arg)
    elif arg[0].lower()=='c':
        imageIds = lib.getImageIds(arg)
    else:
        targetPath = arg

def callCommand(fn):
    "call a command function with <filter> parameters"
    # volnums = None
    # # volnums = config.volumes
    # # imageIds = []
    # imageIds = None
    # targetPath = None
    # for arg in args:
    #     if arg[0] in '0123456789':
    #         volnums = lib.getVolumeNumbers(arg)
    #     elif arg[0].lower()=='c':
    #         imageIds = lib.getImageIds(arg)
    #     else:
    #         targetPath = arg
    # fn(volnums, imageIds, targetPath)
    if volnums:
        for volnum in volnums:
            fn(volnum, None, None)
    if imageIds:
        for imageId in imageIds:
            fn(None, imageId, None)
    if targetPath:
        fn(None, None, targetPath)


if cmd=="download":
    # vols = args[0]
    # volnums = lib.getVolumeNumbers(vols)
    # for volnum in volnums:
    #     vgDownload.vgDownload(volnum, optionOverwrite)
    callCommand(vgDownload.vgDownload)
    lib.beep()


elif cmd=="unzip":
    # vols = args[0]
    # volnums = lib.getVolumeNumbers(vols)
    # for volnum in volnums:
    #     vgUnzip.vgUnzip(volnum, optionOverwrite)
    callCommand(vgUnzip.vgUnzip)
    lib.beep()


elif cmd=="convert":
    # vols = args[0]
    # volnums = lib.getVolumeNumbers(vols)
    # for volnum in volnums:
    #     vgConvert.vgConvert(volnum, optionOverwrite)
    callCommand(vgConvert.vgConvert)
    lib.beep()


elif cmd=="adjust":
    # vols = args[0]
    # volnums = lib.getVolumeNumbers(vols)
    # for volnum in volnums:
    #     vgAdjust.vgAdjust(volnum, optionOverwrite)
    callCommand(vgAdjust.vgAdjust)
    lib.beep()


elif cmd=="denoise":
    # vols = args[0]
    # volnums = lib.getVolumeNumbers(vols)
    # for volnum in volnums:
    #     vgDenoise.vgDenoise(volnum, '', optionOverwrite)
    callCommand(vgDenoise.vgDenoise)
    lib.beep()


elif cmd=="center":
    log.start()
    # arg = args[0]
    # if arg[0].lower()=='c':
    #     imageIds = lib.getImageIds(arg)
    #     for imageId in imageIds:
    #         vgCenter.vgCenter('', imageId, optionOverwrite)
    # else:
    #     vols = arg
    #     volnums = lib.getVolumeNumbers(vols)
    #     for volnum in volnums:
    #         vgCenter.vgCenter(volnum, '', optionOverwrite)
    callCommand(vgCenter.vgCenter)
    log.stop()
    lib.beep()


elif cmd=="composite":
    # arg = args[0]
    # if arg[0].lower()=='c':
    #     compositeIds = lib.getImageIds(arg)
    #     for compositeId in compositeIds:
    #         vgComposite.vgComposite('', compositeId, True)
    # else:
    #     vols = arg
    #     volnums = lib.getVolumeNumbers(vols)
    #     for volnum in volnums:
    #         vgComposite.vgComposite(volnum, '', optionOverwrite)
    callCommand(vgComposite.vgComposite)
    lib.beep()


elif cmd=="target":
    # arg = args[0]
    # if arg[0] in '0123456789':
    #     vols = arg
    #     volnums = lib.getVolumeNumbers(vols)
    #     for volnum in volnums:
    #         vgTarget.vgTarget(volnum, '')
    # else:
    #     targetPath = arg
    #     vgTarget.vgTarget('', targetPath)
    callCommand(vgTarget.vgTarget)
    lib.beep()


elif cmd=="clips":
    # if optionBw==False and optionColor==False:
    #     print 'Must specify -bw or -color'
    # else:
    #     bwOrColor = 'bw' if optionBw else 'color'
    #     # targetpath = args.pop(0)
    #     targetpath = args[0]
    #     vgClips.vgClips(bwOrColor, targetpath, optionKeepLinks)
    #     lib.beep()
    # targetpath = args[0]
    # vgClips.vgClips(targetpath, optionKeepLinks)
    callCommand(vgClips.vgClips)
    lib.beep()


# elif cmd=="segments":
#     targetpath = args[0]
#     vgSegments.vgSegments(targetpath)
#     lib.beep()


elif cmd=="movies":
    # vgMovies.vgMovies()
    callCommand(vgMovies.vgMovies)
    lib.beep()


elif cmd=="list":
    # callCommand(vgList.vgList)
    vgList.vgList(volnums)


elif cmd=="test":
    subject = args[0]
    if subject=='center':
        vgTestCenter.vgTestCenter()
    elif subject=='denoise':
        vgTestDenoise.vgTestDenoise()


elif cmd=="grab":
    vgGrab.vgGrab()


# elif cmd=="uncenter":
#     vols = args[0]
#     volnums = lib.getVolumeNumbers(vols)
#     for volnum in volnums:
#         vgUncenter.vgUncenter(volnum)
#     beep()


elif cmd=="retarget":
    oldTarget = args[0]
    newTarget = args[1]
    vgRetarget.vgRetarget(oldTarget, newTarget)


elif cmd=="init":
    log.start()
    subject = args.pop(0)
    if subject=='files':
        vgInitFiles.vgInitFiles()
    # elif subject=='centers':
    #     vols = args.pop(0)
    #     volnums = lib.getVolumeNumbers(vols)
    #     for volnum in volnums:
    #         vgInitCenters.vgInitCenters(volnum, optionOverwrite)
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
