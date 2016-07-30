
# vg
# voyager command line interface
# --------------------------------------------------------------------------------

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
import vgInitFiles
import vgInitComposites
import vgInitPositions
import vgRetarget
import vgUpdateCenters




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
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgCenter.vgCenter(volnum, overwrite)
    lib.beep()

elif cmd=="composite":
    # vols = args.pop(0)
    # volnums = lib.getVolumeNumbers(vols)
    # for volnum in volnums:
        # vgComposites.buildComposites(volnum, overwrite)
    # lib.beep()
    arg = args.pop(0)
    if arg[0].lower()=='c':
        compositeIds = lib.getImageIds(arg)
        for compositeId in compositeIds:
            vgComposite.vgComposite('', compositeId, True)
    else:
        vols = arg
        volnums = lib.getVolumeNumbers(vols)
        for volnum in volnums:
            # vgComposites.buildComposites(volnum, overwrite)
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

elif cmd=="update":
    subject = args.pop(0)
    if subject=='centers':
        vols = args.pop(0)
        volnums = lib.getVolumeNumbers(vols)
        for volnum in volnums:
            vgUpdateCenters.updateCenters(volnum)
        beep()

elif cmd=="init":
    subject = args.pop(0)
    if subject=='files':
        vgInitFiles.initFiles()
    elif subject=='composites':
        vgInitComposites.initComposites()
    elif subject=='positions':
        vgInitPositions.initPositions()
    lib.beep()

elif cmd=="help":
    pass
else:
    print
    print "Command not recognized."
    cmd = 'help'


if cmd=="help":
    print
    print "Voyager commands"
    print
    print "  vg download <volnums>             - download volume(s)"
    print "  vg unzip <volnums>                - unzip volume(s)"
    print "  vg convert <volnums>              - convert IMGs to PNGs"
    print "  vg adjust <volnums>               - adjust images (rotate and enhance)"
    print "  vg center <volnums>               - center images"
    print "  vg composite <volnums>            - create color images"
    # print "  vg mosaic <volnums>               - create mosaic images"
    print "  vg target <volnums>               - copy images into target subfolders"
    print "  vg clips bw|color [<targetpath>]  - create bw or color clips"
    print "  vg movies                         - create movies from clips"
    print "  vg list                           - show status of local datasets"
    print "  vg test                           - run centering tests"
    print
    # print "  vg init files"
    # print "  vg init composites"
    # print "  vg init mosaics"
    # print
    print "where"
    print
    print "  <volnums> = 5101..5120 Voyager 1 Jupiter"
    print "              6101..6121 Voyager 1 Saturn"
    print "              5201..5214 Voyager 2 Jupiter"
    print "              6201..6215 Voyager 2 Saturn"
    print "              7201..7207 Voyager 2 Uranus"
    print "              8201..8210 Voyager 2 Neptune"
    print "              (ranges and wildcards like 5101-5104 or 51* are ok)"
    print
    print "  <targetpath> = [<system>]/[<spacecraft>]/[<target>]/[<camera>]"
    print "  <system>     = Jupiter|Saturn|Uranus|Neptune"
    print "  <spacecraft> = Voyager1|Voyager2"
    print "  <target>     = Jupiter|Io|Europa|, etc."
    print "  <camera>     = Narrow|Wide"
    print
    print "e.g. vg clips bw //Triton"
    print
    print "You can also add `-y` to a command to have it overwrite any existing data."
    print


