
# vg
# voyager command line interface
# --------------------------------------------------------------------------------

import sys
import os
import inspect

import vg_build


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
    vg_build.buildDownload(volnum)
    
elif cmd=="unzip":
    volnum = args.pop(0)
    vg_build.buildUnzip(volnum)
    
elif cmd=="images":
    volnum = args.pop(0)
    vg_build.buildImages(volnum)
    
elif cmd=="centers":
    volnum = args.pop(0)
    vg_build.buildCenters(volnum)
    
elif cmd=="center":
    centernum = args.pop(0)
    vg_build.buildCenter(centernum)

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
    print
    print "  vg center <centerId>"
    print "  vg composite <compositeId>"
    print "  vg mosaic <mosaicId>"
    print "  vg movie <movieId>"
    print
    print "  vg init images"
    print "  vg init centers"
    print "  vg init composites"
    print "  vg init mosaics"
    print "  vg init movies"
    print
    

# if __name__ == '__main__':
#     main()


# get the absolute path of this file
# see http://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing
# thispath = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

