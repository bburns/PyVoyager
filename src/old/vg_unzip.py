
# unzip voyager targz volumes


import os # for path.isdir

import config
import lib

        
def unzipVolume(volnumber):
    zipfilepath = lib.getZipfilepath(volnumber)
    unzippedpath = lib.getUnzippedpath(volnumber)
    if os.path.isdir(unzippedpath):
        print "Folder exists: " + unzippedpath
        return False
    else:
        print "Unzipping " + zipfilepath
        print "       to " + unzippedpath
        return lib.unzipFile(zipfilepath, unzippedpath)

    
def main():
    # unzip a certain number of volumes
    n = config.nvolumesToUnzip
    for volume in config.volumes:
        if n>0:
            if unzipVolume(volume):
                n -= 1
                
if __name__ == '__main__':
    main()
        


