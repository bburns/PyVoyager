
# download voyager image archives


# import os # for system
import os.path # for isfile
# import urllib # for urlretrieve
# import requests # for get, for progressbar
# import sys # for stdout

import config
import lib

        
def downloadVolume(volnumber, folder=config.downloadFolder):
    "download a voyager image volume to the given folder"
    # eg downloadVolume(5101)
    url = lib.getDownloadUrl(volnumber)
    zipfilepath = lib.getZipfilepath(volnumber)
    filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    filepath = folder + "/" + filetitle
    if os.path.isfile(filepath):
        print "File exists: " + filepath
        return False
    else:
        print "Downloading " + url
        print "         to " + filepath
        return lib.downloadFile(url, filepath)
        # return True
    

if __name__ == '__main__':
    # download a certain number of volumes
    n = config.nvolumesToDownload
    for volume in config.volumes:
        if n>0:
            if downloadVolume(volume):
                n -= 1
                
    
    
