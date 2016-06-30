
# download voyager image archives


# import os # for system
import os.path # for isfile
# import urllib # for urlretrieve
# import requests # for get, for progressbar
# import sys # for stdout

import config
import lib

        
def download_volume(volnumber, folder=config.download_folder):
    "download a voyager image volume to the given folder"
    # eg download_volume(5101)
    url = lib.get_download_url(volnumber)
    zipfilepath = lib.get_zipfilepath(volnumber)
    filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    filepath = folder + "/" + filetitle
    if os.path.isfile(filepath):
        print "File exists: " + filepath
        return False
    else:
        print "Downloading " + url
        print "         to " + filepath
        return lib.download_file(url, filepath)
        # return True
    

if __name__ == '__main__':
    # download a certain number of volumes
    for volume in config.volumes:
        if config.nvolumes_to_download>0:
            if download_volume(volume):
                config.nvolumes_to_download -= 1
                
    
    
