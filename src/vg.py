
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

 
# call relevant routines in vg_build.py
if cmd=="download":
    volnum = args.pop(0)
    vgBuildDownload.buildDownload(volnum)
    
elif cmd=="unzip":
    volnum = args.pop(0)
    vgBuildUnzip.buildUnzip(volnum)
    
elif cmd=="images":
    volnum = args.pop(0)
    vgBuildImages.buildImages(volnum)
    
elif cmd=="centers":
    volnum = args.pop(0)
    vgBuildCenters.buildCenters(volnum)
    
elif cmd=="composites":
    volnum = args.pop(0)
    vgBuildComposites.buildComposites(volnum)
    
elif cmd=="targets":
    volnum = args.pop(0)
    vgBuildTargets.buildTargets(volnum)
    # targetPath = args.pop(0)
    # vgBuild.buildTargets(targetPath)
    
elif cmd=="movies":
    targetPath = args.pop(0)
    vgBuildMovies.buildMovies(targetPath)
    
    
elif cmd=="init":
    noun = args.pop(0)
    if noun=='files':
        vgInitFiles.initFiles()
    elif noun=='composites':
        vgInitComposites.initComposites()
    
# elif cmd=="center":
#     centernum = args.pop(0)
#     vgBuild.buildCenter(centernum)

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
    print "  vg mosaics <volnumber>"
    print "  vg targets <volnumber>"
    print
    print "  vg movies <system>/<spacecraft>/<target>/<camera>"
    print
    # print "  vg center <centerId>"
    # print "  vg composite <compositeId>"
    # print "  vg mosaic <mosaicId>"
    # print "  vg movie <movieId>"
    # print
    print "  vg init files"
    # print "  vg init images"
    # print "  vg init centers"
    # print "  vg init composites"
    # print "  vg init mosaics"
    # print "  vg init movies"
    print
    

# if __name__ == '__main__':
#     main()


# get the absolute path of this file
# see http://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing
# thispath = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

