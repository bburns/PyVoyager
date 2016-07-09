
import os
import csv

import config
import lib


def buildTargets(targetPath):
    "copy/link images to correct subfolders (eg Jupiter/Voyager1/Io/Narrow)"
    
    #.. if we make these links then will automatically update when recenter images/tweak composite colors etc
    # same with movie frames, so would just need to do vg movie to generate corrected movie
    
    # iterate down files.txt
    # if target path matches row,
    # copy that image to new subfolder
    
    #. assume these are all None for now
    # ie just copy ALL images available
    # [system, craft, target, camera] = targetPath.split('/')
    
    # files.txt:
    # volume,fileid,phase,craft,target,instrument,filter,note
    # VGISS_5101,C1385455,Jupiter,Voyager1,Dark,Wide,CLEAR,DARK CURRENT CALIBRATION
    
    # columns in files.txt
    filesColVolume = 0
    filesColFileId = 1
    filesColPhase = 2
    filesColCraft = 3
    filesColTarget = 4
    filesColInstrument = 5
    filesColFilter = 6
    filesColNote = 7
    
    f = open(config.filesdb, 'rt')
    i = 0
    item = {}
    try:
        reader = csv.reader(f)
        for row in reader:
            if i==0:
                fields = row
            else:
                volume = row[filesColVolume]
                fileid = row[filesColFileId]
                filter = row[filesColFilter]
                
                # get subfolder, eg ../data/step3_centers/VGISS_5101
                centersSubfolder = config.centersFolder + '/' + volume
                
                # get source filename
                # eg centered_C1327321_RAW_ORANGE.PNG
                centeredfilename = config.centersprefix + fileid + '_' + config.filetype + '_' + filter + '.PNG' 
                src = centersSubfolder + '/' + centeredfilename

                # if file exists, create subfolder and copy/link image
                if os.path.isfile(src):

                    # get subfolder, eg Jupiter/Voyager1/Io/Narrow
                    phase = row[filesColPhase]
                    craft = row[filesColCraft]
                    target = row[filesColTarget]
                    instrument = row[filesColInstrument]
                    subfolder = phase +'/' + craft + '/' + target +'/' + instrument 
                    # eg ../data/step7_targets/jupiter/voyager1/io/narrow
                    targetpath = config.targetsFolder + '/' + subfolder 
                    
                    # skip if file already exists (to save time on copying)
                    targetfile = targetpath + '/' + centeredfilename
                    if True:
                    # if not os.path.isfile(targetfile):
                    
                        # create subfolder
                        lib.mkdir_p(targetpath)

                        # copy file
                        # cp -s, --symbolic-link - make symbolic links instead of copying [but is ignored on windows]
                        #. mklink requires admin privileges - handle later
                        cmd = 'cp ' + src + ' ' + targetpath
                        print cmd
                        os.system(cmd)

            i += 1

    finally:
        f.close()
    
