
# copy png files to target/instrument subfolders

import os # for system
# import os.path # for isfile, join
import csv

import config
import lib

        
def moveVolumeToSubfolders(volnumber):
    "move a volume's png files to correct subfolders (eg jupiter/voyager1/jupiter/narrow)"
    
    # iterate down the giant csv file
    # if the row matches this volume number,
    # get the craft, flyby, target, camera
    # and attempt to move the row's file to a new subfolder
    
    voltitle = lib.getVolumeTitle(volnumber)
    centersfolder = config.centersFolder + '/' + voltitle
    
    f = open(config.indexfile, 'rt')
    try:
        reader = csv.reader(f)
        for row in reader:
            filename = row[config.col_filename].strip()
            ext = filename.split('.')[1]
            
            # get image files
            if ext=='IMG':
                
                # get field values
                craft = row[config.col_craft].strip()
                phase = row[config.col_phase].strip()
                target = row[config.col_target].strip()
                instrument = row[config.col_instrument].strip()
                filter = row[config.col_filter].strip()
                
                # translate field values
                craft = config.translations[craft]
                phase = config.translations[phase]
                target = target.title()
                instrument = config.translations[instrument]
                
                # create subfolder
                subfolder = config.subfolderFolder + '/' + phase +'/' + target +'/' + instrument # eg Jupiter/Io/Narrow
                lib.mkdir_p(subfolder)
                
                # add filter name
                filename = 'centered_' + filename.split('.')[0] + '_' + filter + '.PNG' # eg centered_foo_ORANGE.PNG
                
                # attempt to copy file
                # eg 'cp ../data/step3_pngs/foo_ORANGE.png ../data/step4_folders/
                src = centersfolder + '/' + filename
                cmd = 'cp ' + src + ' ' + subfolder
                print cmd
                os.system(cmd)
                
    finally:
        f.close()
    
    # url = lib.getDownloadUrl(volnumber)
    # zipfilepath = lib.getZipfilepath(volnumber)
    # filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    # filepath = folder + "/" + filetitle
    # if os.path.isfile(filepath):
    #     print "File exists: " + filepath
    #     return False
    # else:
    #     print "Downloading " + url
    #     print "         to " + filepath
    #     return lib.downloadFile(url, filepath)
    #     # return True
    

if __name__ == '__main__':
    moveVolumeToSubfolders(5102)
    
    # # download a certain number of volumes
    # n = config.nvolumesToDownload
    # for volume in config.volumes:
    #     if n>0:
    #         if downloadVolume(volume):
    #             n -= 1
                
    
    
