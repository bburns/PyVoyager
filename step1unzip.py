
# unzip voyager targz volumes


import os # for path.isdir

import config
import lib

        
def unzip_volume(volnumber):
    zipfilepath = lib.get_zipfilepath(volnumber)
    unzippedpath = lib.get_unzippedpath(volnumber)
    if os.path.isdir(unzippedpath):
        print "Folder exists: " + unzippedpath
        return False
    else:
        print "Unzipping " + zipfilepath
        print "         to " + unzippedpath
        return lib.unzip_file(zipfilepath, unzippedpath)
        return True


if __name__ == '__main__':
    # unzip a certain number of volumes
    for volume in config.volumes:
        if config.nvolumes_to_unzip>0:
            if unzip_volume(volume):
                config.nvolumes_to_unzip -= 1
                
        


