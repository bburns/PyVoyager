
# convert voyager img files to pngs, using img2png
# --------------------------------------------------------------------------------

# currently,
# cd to the datavolume, eg VGISS_5101
# > vr unzip
# by default it'll start in the data dir, and convert all "*raw.img" files to pngs,
# appending the filter name. 

import config
import lib


#. do all imagetypes
# imagetypes = ['RAW', 'CLEANED', 'CALIB', 'GEOMED']
# imagetype = "RAW"
# filespec = "*" + imagetype + ".img"
# filespec = "*" # do all image types

img2pngOptions = "-fnamefilter" # append filter name, eg _ORANGE



def img2pngVolume(volnumber):
    "convert img files in a voyager volume to pngs"
    import os
    import os.path
    unzippedpath = lib.getUnzippedpath(volnumber)
    pngpath = lib.getPngpath(volnumber)
    if os.path.isdir(pngpath):
        print "Folder exists: " + pngpath
        return False
    else:
        lib.mkdir(pngpath) # create folder
        datadir = unzippedpath + '/DATA'
        print "converting imgs to pngs for " + datadir
        # for each dir in thisdir, cd dir, run img2png on all img files
        i = 0
        for root, dirs, files in os.walk(datadir):
            for subdir in dirs:
                dirpath = os.path.join(root, subdir)
                dirpath = os.path.abspath(dirpath)
                print 'dir ' + str(i) + ': ' + dirpath
                filespec = "*" # do all image types
                lib.img2png(dirpath, filespec, pngpath)
                i += 1
        return True
    

def main():
    
    # img2pngVolume(5102)
    
    # convert a certain number of volumes
    n = config.nvolumesToPng
    for volume in config.volumes:
        if n>0:
            if img2pngVolume(volume):
                n -= 1
                

if __name__ == '__main__':
    main()

