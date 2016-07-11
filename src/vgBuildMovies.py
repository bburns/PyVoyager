
# build movies associated with target subfolders,
# eg Jupiter/Voyager1/Io/Narrow


import csv

import config
import lib



def buildMovies(targetPath):
    "build movies associated with the given target path (eg Jupiter/Voyager1/Io/Narrow)"
    # eg buildMovies("Jupiter")

    # this will be similar to buildtargets, but make links instead of copying files
    # and number them sequentially also
    
    #. for now say they're all on
    # parts = targetPath.split('/')
    # while len(parts)<4:
        # parts.append(None)
    # print parts
    # pathSystem, pathCraft, pathTarget, pathCamera = parts
    pathSystem, pathCraft, pathTarget, pathCamera = [None,None,None,None]

    # iterate through all files
    f = open(config.filesdb, 'rt')
    i = 0
    reader = csv.reader(f)
    for row in reader:
        if i==0:
            fields = row
        else:
            volume = row[config.filesColVolume]
            fileid = row[config.filesColFileId]
            filter = row[config.filesColFilter]

            # get subfolder, eg data/step3_centers/VGISS_5101
            centersSubfolder = config.centersFolder + '/' + volume

            # get source filename and path
            # eg centered_C1327321_RAW_ORANGE.PNG
            # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
            centeredfilename = config.centersprefix + fileid + '_' + config.imageType + '_' + filter + '.PNG' 
            centeredpath = centersSubfolder + '/' + centeredfilename

            # if file exists, create subfolder and copy/link image
            if os.path.isfile(centeredpath):

                system = row[config.filesColPhase]
                craft = row[config.filesColCraft]
                target = row[config.filesColTarget]
                camera = row[config.filesColInstrument]

                # get subfolder, eg Jupiter/Voyager1/Io/Narrow
                subfolder = system +'/' + craft + '/' + target +'/' + camera 

                # get target file, eg data/step7_targets/jupiter/voyager1/io/narrow/centered_.....png
                targetpath = config.targetsFolder + '/' + subfolder
                targetfile = targetpath + '/' + centeredfilename

                # skip if file already exists (to save time on copying)
                if True:
                # if not os.path.isfile(targetfile):

                    # create subfolder
                    lib.mkdir_p(targetpath)

                    # # copy file
                    # # cp -s, --symbolic-link - make symbolic links instead of copying [but ignored on windows]
                    # cmd = 'cp ' + centeredpath + ' ' + targetpath
                    # print cmd
                    # os.system(cmd)

                    # links work, but then can't browse folders with image viewer... so back to copying
                    # link to file
                    # note: mklink requires admin privileges, so must run this script in an admin console
                    # eg ../data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
                    src2 = '../../../../../' + src # need to get out of the target dir
                    cmd = 'mklink ' + targetfile + ' ' + src2
                    cmd = cmd.replace('/','\\')
                    print cmd
                    os.system(cmd)

        i += 1

    f.close()
    
    # filein = open(config.filesdb, 'rt')
    # reader = csv.reader(filein)
    # for row in reader:
    #     row = [field.strip() for field in row]

    #     # get field values
    #     volume = row[config.indexFileColVolume] # eg VGISS_5101
    #     filename = row[config.indexFileColFilename] # eg C1385455_RAW.IMG
    #     craft = row[config.indexFileColCraft] # eg VOYAGER 1
    #     phase = row[config.indexFileColPhase] # eg JUPITER ENCOUNTER
    #     target = row[config.indexFileColTarget] # eg N RINGS
    #     time = row[config.indexFileColTime] # eg 1979-03-05T15:32:56
    #     instrument = row[config.indexFileColInstrument] # eg NARROW ANGLE CAMERA
    #     filter = row[config.indexFileColFilter] # eg ORANGE
    #     note = row[config.indexFileColNote] 

    #     # translate where needed
    #     fileid = filename.split('_')[0] # eg C1385455
    #     phase = config.indexTranslations[phase] # eg Jupiter
    #     craft = config.indexTranslations[craft] # eg Voyager1
    #     instrument = config.indexTranslations[instrument] # eg Narrow
    #     target = target.title().replace(' ','_') # eg N_Rings

    #     # write row
    #     row = [volume, fileid, phase, craft, target, time, instrument, filter, note] # keep in sync with fields, above
    #     # print row # too slow
    #     writer.writerow(row)
    


if __name__ == '__main__':
    buildMovies("Neptune")
    print 'done'


    
    
    
    
    
    
#. top-down approach, for later, when get movies.txt working

    # # need to lookup the contents of the movie in the movies.txt db
    # # for each frame, call buildItem, which will dispatch on the item type and recurse
    # # then at the end of the list, stage the images and run ffmpeg on them

    # filenamePattern = 'img%05d.png'

    # # so need to open movies.txt, scan through rows till find movieId,
    # # gather all child_ids and params
    # # call buildItem with the id and params
    # filein = open(config.moviesdb, 'rt')
    # i = 0
    # try:
    #     reader = csv.reader(filein)
    #     for row in reader:
    #         if i==0:
    #             pass
    #         else:
    #             movieId = row[0]
    #             # if movieId==
    #             childId = row[1]
    #             buildItem(childId)
    #             #. copy item to sequential staging folder
    #             print 'copy item', filenamePattern % i
    #             i += 1
    # finally:
    #     filein.close()
    
    # # need to stage all the files first, numbering them sequentially
    # # copy them to a folder like step4_movies/movie1/
    # # will need to do individually, as each image could be located in a different folder
    
    # # voltitle = lib.getVolumeTitle(volnum) # eg VGISS_5101
    # # src = config.centersFolder + '/' + voltitle
    # # dst = config.moviesFolder + '/' + voltitle
    
    # # # stage files for ffmpeg
    # # filenamePattern = 'img%04d.png'
    # # lib.copyFilesSequenced(src, dst, filenamePattern)
    
    # # # now make movie with ffmpeg
    # # movieName = '_' + voltitle + '.mp4' # prepend _ so sorts at start of file list
    # # lib.pngsToMp4(dst, filenamePattern, movieName, config.frameRate)
