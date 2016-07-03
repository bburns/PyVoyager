
# convert voyager img files to pngs, using img2png
# --------------------------------------------------------------------------------

# currently,
# cd to the datavolume, eg VGISS_5101
# > vr unzip
# by default it'll start in the data dir, and convert all "*raw.img" files to pngs,
# appending the filter name. 

import config
import lib


imagetype = "RAW" # CALIB, CLEANED, GEOMED, or RAW
filespec = "*" + imagetype + ".img"
img2png_options = "-fnamefilter" # append filter name, eg _ORANGE


def img2png(dirpath):
    "convert all img files matching filespec to png files"
    import os
    # savedir = os.getcwd()
    os.chdir(dirpath)
    # eg "img2png *.img -fnamefilter"
    cmd = "img2png " + filespec + " " + img2png_options
    print cmd
    os.system(cmd)
    # os.chdir(savedir)


def img2png_volume(volnumber):
    "convert img files in a voyager volume to pngs"
    import os
    import os.path
    unzippedpath = lib.get_unzippedpath(volnumber)
    pngpath = lib.get_pngpath(volnumber)
    if os.path.isdir(pngpath):
        print "Folder exists: " + pngpath
        return False
    else:
        datadir = unzippedpath + '/DATA'
        print "converting imgs to pngs for " + datadir
        # for each dir in thisdir, cd dir, run img2png on all img files
        i = 0
        for root, dirs, files in os.walk(datadir):
            for subdir in dirs:
                dirpath = os.path.join(root, subdir)
                dirpath = os.path.abspath(dirpath)
                print 'dir ' + str(i) + ': ' + dirpath
                img2png(dirpath)
                # now move the png files to pngpath
                # make sure folder exists first
                try:
                    os.mkdir(pngpath) 
                except:
                    pass
                cmd = "move " + dirpath +"\\*.png " + pngpath + "/"
                print cmd
                os.system(cmd)
                i += 1
        return True
    

def main():
    
    # img2png_volume(5102)
    
    # convert a certain number of volumes
    n = config.nvolumes_to_png
    for volume in config.volumes:
        if n>0:
            if img2png_volume(volume):
                n -= 1
                

if __name__ == '__main__':
    main()

