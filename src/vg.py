
# vg
# voyager command line interface
# --------------------------------------------------------------------------------

import sys
import os
import inspect
import tabulate
import re

import config
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
    
# elif cmd=="list":
#     # build a dictionary of {5101: {'Downloads':True,'Unzips':False,...}, }
#     # then convert to an array of arrays
#     # print tabulate.tabulate([['Alice', 24], ['Bob', 19]], headers=['Name', 'Age'])
#     headers = ['Volume', 'Downloads', 'Unzips', 'Images', 'Centers', 'Composites']
#     rows = []
#     for vol in config.volumes:
#         # only include a row if it has some data
#         row = [vol]
#         rows.append(row)
#     print tabulate.tabulate(rows, headers)
    
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
    # print "  vg list - show listing of datasets available for each step"
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


def getVolumeNumbers(s):
    "parse a string like 5101-5108 or 5104 or 51* to an array of volnum strings"
    # eg getVolumeNumber('5201-5203') => [5201,5202,5203]
    
    # handle ranges, eg 8201-8204
    vols = s.split('-')
    if len(vols)==2:
        vols = [int(vol) for vol in vols]
        volrange = range(vols[0],vols[1]+1)
        return volrange # eg [8201,8202,8203,8204]

    # handle invidual volumes or wildcards
    sregex = s.replace('*','.*') # eg '52.*'
    regex = re.compile(sregex)
    vols = []
    svolumes = [str(vol) for vol in config.volumes] # all available volumes
    for svolume in svolumes:
        if re.match(regex, svolume):
            vols.append(int(svolume))
    return vols


# if __name__ == '__main__':
#     os.chdir('..')
#     print getVolumeNumbers('5104')
#     print getVolumeNumbers('5104-5108')
#     print getVolumeNumbers('51*')
#     print getVolumeNumbers('5*')
#     print getVolumeNumbers('*')
#     print 'done'

