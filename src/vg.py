
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
import vgComposite
import vgMosaic
import vgAnnotate
import vgTarget
import vgClips
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

# pick out and remove options from argument list
optionOverwrite = False
optionKeepLinks = False
optionList = [arg for arg in args if arg[0]=='-']
args = [arg for arg in args if arg[0]!='-']
for option in optionList:
    if option=='-y':
        optionOverwrite = True
    elif option=='-keeplinks':
        optionKeepLinks = True

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

elif cmd=="composite":
    if filterImageIds:
        for compositeId in filterImageIds:
            vgComposite.vgComposite('', compositeId, optionOverwrite=True)
    else:
        for filterVolume in filterVolumes:
            vgComposite.vgComposite(filterVolume, '', optionOverwrite)
    lib.beep()

elif cmd=="mosaic":
    for filterVolume in filterVolumes:
        vgMosaic.vgMosaic(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="annotate":
    for filterVolume in filterVolumes:
        vgAnnotate.vgAnnotate(filterVolume, optionOverwrite)
    lib.beep()

elif cmd=="target":
    if filterVolumes:
        for filterVolume in filterVolumes:
            vgTarget.vgTarget(filterVolume, '')
    else:
        vgTarget.vgTarget('', filterTargetPath)
    lib.beep()

elif cmd=="clips":
    if filterVolumes is None:
        filterVolumes = config.volumes
    vgClips.vgClips(filterVolumes, filterTargetPath, optionKeepLinks)
    lib.beep()

elif cmd=="movies":
    vgMovies.vgMovies()
    lib.beep()

elif cmd=="list":
    vgList.vgList(filterVolumes)

elif cmd=="test":
    subject = args[0]
    if subject=='center':
        vgTestCenter.vgTestCenter()
    elif subject=='denoise':
        vgTestDenoise.vgTestDenoise()

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
