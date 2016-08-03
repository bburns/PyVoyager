
# vg
# voyager command line interface

"""
PyVoyager commands

  vg download <volnums>             - download volume(s)
  vg unzip <volnums>                - unzip volume(s)
  vg convert <volnums>              - convert IMGs to PNGs
  vg adjust <volnums>               - adjust images (rotate and enhance)
  vg center <volnums>               - center images
  vg composite <volnums>            - create color images
  vg target <volnums>               - copy images into target subfolders
  vg clips bw|color [<targetpath>]  - create bw or color clips
  vg movies                         - create movies from clips
  vg list                           - show status of local datasets
  vg test                           - run centering tests

where

  <volnums> = 5101..5120 Voyager 1 Jupiter
              6101..6121 Voyager 1 Saturn
              5201..5214 Voyager 2 Jupiter
              6201..6215 Voyager 2 Saturn
              7201..7207 Voyager 2 Uranus
              8201..8210 Voyager 2 Neptune
              (ranges and wildcards like 5101-5104 or 51* are ok)

  <targetpath> = [<system>]/[<spacecraft>]/[<target>]/[<camera>]
  <system>     = Jupiter|Saturn|Uranus|Neptune
  <spacecraft> = Voyager1|Voyager2
  <target>     = Jupiter|Io|Europa|, etc.
  <camera>     = Narrow|Wide

e.g. vg clips bw //Triton

You can also add `-y` to a command to have it overwrite any existing data.
"""

import sys
import os
import inspect
import tabulate
import re

import config
import lib
import vgDownload
import vgUnzip
import vgConvert
import vgAdjust
import vgCenter
import vgComposite
import vgMosaic
import vgTarget
import vgClips
import vgSegments
import vgMovies
import vgList
import vgTest
import vgGrab
import vgInitFiles
import vgInitCenters
import vgInitComposites
import vgInitPositions
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
overwrite = False
options = [arg for arg in args if arg[0]=='-']
args = [arg for arg in args if arg[0]!='-']
for option in options:
    if option=='-y':
        overwrite = True

if cmd=="download":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgDownload.vgDownload(volnum, overwrite)
    lib.beep()

elif cmd=="unzip":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgUnzip.vgUnzip(volnum, overwrite)
    lib.beep()

elif cmd=="convert":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgConvert.vgConvert(volnum, overwrite)
    lib.beep()

elif cmd=="adjust":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgAdjust.vgAdjust(volnum, overwrite)
    lib.beep()

elif cmd=="center":
    arg = args.pop(0)
    if arg[0].lower()=='c':
        imageIds = lib.getImageIds(arg)
        for imageId in imageIds:
            vgCenter.vgCenter('', imageId, True)
    else:
        vols = arg
        volnums = lib.getVolumeNumbers(vols)
        for volnum in volnums:
            vgCenter.vgCenter(volnum, '', overwrite)
    lib.beep()

elif cmd=="composite":
    arg = args.pop(0)
    if arg[0].lower()=='c':
        compositeIds = lib.getImageIds(arg)
        for compositeId in compositeIds:
            vgComposite.vgComposite('', compositeId, True)
    else:
        vols = arg
        volnums = lib.getVolumeNumbers(vols)
        for volnum in volnums:
            vgComposite.vgComposite(volnum, '', overwrite)
    lib.beep()

elif cmd=="target":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgTarget.vgTarget(volnum)
    # targetPath = args.pop(0)
    # vg.buildTargets(targetPath)
    lib.beep()

elif cmd=="retarget":
    oldTarget = args.pop(0)
    newTarget = args.pop(0)
    vgRetarget.vgRetarget(oldTarget, newTarget)

elif cmd=="clips":
    bwOrColor = None
    target = None
    if nargs>=2:
        bwOrColor = args.pop(0)
    if nargs==3:
        targetpath = args.pop(0)
    if bwOrColor=='bw' or bwOrColor=='color':
        vgClips.vgClips(bwOrColor, targetpath)
    else:
        cmd="help"
    lib.beep()

elif cmd=="segments":
    targetpath = args.pop(0)
    vgSegments.vgSegments(targetpath)
    lib.beep()

elif cmd=="movies":
    vgMovies.vgMovies()
    lib.beep()

elif cmd=="list":
    vgList.vgList()

elif cmd=="test":
    vgTest.vgTest()

elif cmd=="grab":
    vgGrab.vgGrab()

elif cmd=="uncenter":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgUncenter.vgUncenter(volnum)
    beep()

elif cmd=="init":
    subject = args.pop(0)
    if subject=='files':
        vgInitFiles.vgInitFiles()
    elif subject=='centers':
        vols = args.pop(0)
        volnums = lib.getVolumeNumbers(vols)
        for volnum in volnums:
            vgInitCenters.vgInitCenters(volnum)
    elif subject=='composites':
        vgInitComposites.vgInitComposites()
    elif subject=='positions':
        vgInitPositions.vgInitPositions()
    lib.beep()

elif cmd=="help":
    pass
else:
    print
    print "Command not recognized."
    cmd = 'help'

if cmd=="help":
    print __doc__
