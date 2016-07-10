
import os
import csv

import config
import lib


# def buildTargets(targetPath):
    # "copy/link images to target subfolders (eg Jupiter/Voyager1/Io/Narrow)"
    # assume these are all None for now
    # ie just copy ALL images available
    # [system, craft, target, camera] = targetPath.split('/')
    
def buildTargets(volnum):
    "copy/link images in volume to target subfolders"
    
    # if we make these links then will automatically update when recenter images/tweak composite colors etc
    # same with movie frames, so would just need to do vg movie to generate corrected movie
    # (but wouldn't work with image viewer)
    
    # iterate down files.txt
    # if target path matches row,
    # copy that image to target subfolder
    
    volid = lib.getVolumeTitle(volnum) # eg VGISS_5101
    
    # files.txt:
    # volume,fileid,phase,craft,target,instrument,filter,note
    # VGISS_5101,C1385455,Jupiter,Voyager1,Dark,Wide,CLEAR,DARK CURRENT CALIBRATION
    
    f = open(config.filesdb, 'rt')
    i = 0
    # item = {}
    try:
        reader = csv.reader(f)
        for row in reader:
            if i==0:
                fields = row
            else:
                volume = row[config.filesColVolume]
                if volume==volid:
                    fileid = row[config.filesColFileId]
                    filter = row[config.filesColFilter]

                    # get subfolder, eg ../data/step3_centers/VGISS_5101
                    centersSubfolder = config.centersFolder + '/' + volume

                    # get source filename
                    # eg centered_C1327321_RAW_ORANGE.PNG
                    centeredfilename = config.centersprefix + fileid + '_' + config.imageType + '_' + filter + '.PNG' 
                    # eg ../data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
                    src = centersSubfolder + '/' + centeredfilename

                    # if file exists, create subfolder and copy/link image
                    if os.path.isfile(src):

                        # get subfolder, eg Jupiter/Voyager1/Io/Narrow
                        phase = row[config.filesColPhase]
                        craft = row[config.filesColCraft]
                        target = row[config.filesColTarget]
                        instrument = row[config.filesColInstrument]
                        subfolder = phase +'/' + craft + '/' + target +'/' + instrument 
                        
                        # get target file, eg ../data/step7_targets/jupiter/voyager1/io/narrow/centered_....
                        targetpath = config.targetsFolder + '/' + subfolder
                        targetfile = targetpath + '/' + centeredfilename

                        # skip if file already exists (to save time on copying)
                        if True:
                        # if not os.path.isfile(targetfile):

                            # create subfolder
                            lib.mkdir_p(targetpath)

                            # copy file
                            # cp -s, --symbolic-link - make symbolic links instead of copying [but ignored on windows]
                            cmd = 'cp ' + src + ' ' + targetpath
                            print cmd
                            os.system(cmd)

                            # links work, but then can't browse folders with image viewer... so back to copying
                            # # link to file
                            # # note: mklink requires admin privileges, so must run this script in an admin console
                            # # eg ../data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
                            # src2 = '../../../../../' + src # need to get out of the target dir
                            # cmd = 'mklink ' + targetfile + ' ' + src2
                            # cmd = cmd.replace('/','\\')
                            # print cmd
                            # os.system(cmd)

            i += 1

    finally:
        f.close()
    
