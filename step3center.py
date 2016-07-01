
# center images on planet

import os

import config
import lib
import libimg


prefix = 'centered_'


def center_volume(volnumber):
    pngpath = lib.get_pngpath(volnumber)
    centeredpath = lib.get_centeredpath(volnumber)
    if os.path.isdir(centeredpath):
        print "Folder exists: " + pngpath
        return False
    else:
        try:
            os.mkdir(centeredpath) 
        except:
            pass
        for root, dirs, files in os.walk(pngpath):
            for filename in files:
                ext = filename[-4:]
                if ext=='.png':
                    infile = pngpath + '/' + filename
                    print infile
                    outfile = centeredpath + '/' + prefix + filename
                    # print '  ' + outfile
                    libimg.center_image_file(infile, outfile, config.rotate_image)
        return True


def main():
    # center a certain number of volumes
    n = config.nvolumes_to_center
    for volume in config.volumes:
        if n>0:
            if center_volume(volume):
                n -= 1
                
if __name__ == '__main__':
    main()


