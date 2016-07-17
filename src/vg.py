
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
import vgBuildDownload
import vgBuildUnzip
import vgBuildImages
import vgBuildCenters
import vgBuildComposites
import vgBuildMosaics
import vgBuildTargets
import vgBuildList
import vgBuildMovies
import vgInitFiles
import vgInitComposites


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
        vgBuildDownload.buildDownload(volnum, overwrite)

elif cmd=="unzip":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgBuildUnzip.buildUnzip(volnum, overwrite)

elif cmd=="images":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgBuildImages.buildImages(volnum, overwrite)

elif cmd=="centers":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgBuildCenters.buildCenters(volnum, overwrite)

elif cmd=="composites":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgBuildComposites.buildComposites(volnum, overwrite)

elif cmd=="targets":
    vols = args.pop(0)
    volnums = lib.getVolumeNumbers(vols)
    for volnum in volnums:
        vgBuildTargets.buildTargets(volnum)
    # targetPath = args.pop(0)
    # vgBuild.buildTargets(targetPath)

elif cmd=="list":
    vgBuildList.buildList()

elif cmd=="movies":
    bwOrColor = None
    target = None
    if nargs>=2:
        bwOrColor = args.pop(0)
    if nargs==3:
        targetpath = args.pop(0)
    if bwOrColor=='bw' or bwOrColor=='color':
        vgBuildMovies.buildMovies(bwOrColor, targetpath)
    else:
        cmd="help"

elif cmd=="init":
    subject = args.pop(0)
    if subject=='files':
        vgInitFiles.initFiles()
    elif subject=='composites':
        vgInitComposites.initComposites()

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
    print "  vg images <volnums>               - convert IMGs to PNGs"
    print "  vg centers <volnums>              - center images"
    print "  vg composites <volnums>           - create color images"
    # print "  vg mosaics <volnums>              - create mosaic images"
    print "  vg targets <volnums>              - copy images into target subfolders"
    print "  vg list                           - show status of local datasets"
    print "  vg movies bw|color [<targetpath>] - create bw or color movies"
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
    print
    print "  <system>     = Jupiter|Saturn|Uranus|Neptune"
    print "  <spacecraft> = Voyager1|Voyager2"
    print "  <target>     = Jupiter|Io|Europa|, etc."
    print "  <camera>     = Narrow|Wide"
    print
    print "e.g. `vg movies bw //Triton`"
    print
    print "You can also add `-y` to a command to have it overwrite any existing data."
    print


