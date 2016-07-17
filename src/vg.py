
# vg
# voyager command line interface
# --------------------------------------------------------------------------------

import sys
import os
import inspect

import vgBuildDownload
import vgBuildUnzip
import vgBuildImages
import vgBuildCenters
import vgBuildComposites
import vgBuildMosaics
import vgBuildTargets
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

# pick out options
overwrite = False
options = [arg for arg in args if arg[0]=='-']
args = [arg for arg in args if arg[0]!='-']
for option in options:
    if option=='-y':
        overwrite = True


if cmd=="download":
    volnum = args.pop(0)
    vgBuildDownload.buildDownload(volnum, overwrite)
    
elif cmd=="unzip":
    volnum = args.pop(0)
    vgBuildUnzip.buildUnzip(volnum, overwrite)
    
elif cmd=="images":
    volnum = args.pop(0)
    vgBuildImages.buildImages(volnum, overwrite)
    
elif cmd=="centers":
    volnum = args.pop(0)
    vgBuildCenters.buildCenters(volnum, overwrite)
    
elif cmd=="composites":
    volnum = args.pop(0)
    vgBuildComposites.buildComposites(volnum, overwrite)
    
elif cmd=="targets":
    volnum = args.pop(0)
    vgBuildTargets.buildTargets(volnum)
    # targetPath = args.pop(0)
    # vgBuild.buildTargets(targetPath)
    
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
    print "  vg download <volnumber>"
    print "  vg unzip <volnumber>"
    print "  vg images <volnumber>"
    print "  vg centers <volnumber>"
    print "  vg composites <volnumber>"
    # print "  vg mosaics <volnumber>"
    print "  vg targets <volnumber>"
    print
    # print "  vg movies <system>/<spacecraft>/<target>/<camera>"
    print "  vg movies bw|color [<targetpath>]"
    print
    # print "  vg center <centerId>"
    # print "  vg composite <compositeId>"
    # print "  vg mosaic <mosaicId>"
    # print "  vg movie <movieId>"
    # print
    # print "  vg init files"
    # print "  vg init images"
    # print "  vg init centers"
    # print "  vg init composites"
    # print "  vg init mosaics"
    # print "  vg init movies"
    # print
    print "where"
    print
    print "  <volnumber>  = 5101..5120 Voyager 1 Jupiter"
    print "                 6101..6121 Voyager 1 Saturn"
    print "                 5201..5214 Voyager 2 Jupiter"
    print "                 6201..6215 Voyager 2 Saturn"
    print "                 7201..7207 Voyager 2 Uranus"
    print "                 8201..8210 Voyager 2 Neptune"
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

