
# build movies associated with target subfolders,
# eg Jupiter/Voyager1/Io/Narrow


import csv
import os
import os.path

import config
import lib



filespec = 'img%05d.png'

def renameFilesSequentially():
    ""
    # now need to go through and rename files sequentially for ffmpeg
    # for each subdir in datadir, cd subdir, run img2png on all img files in it
    print 'rename files sequentially'
    folder = config.moviesFolder
    for root, dirs, files in os.walk(folder):
        # print root, dirs
        if dirs==[]: # reached the leaf level
            # print root
            i = 1
            for filename in files:
                dest = filespec % i
                if filename!=dest:
                    filepath = root + '\\' + filename
                    destpath = root + '\\' + dest
                    # print 'rename ' + filepath + ' -> ' + dest
                    # cmd = 'mv ' + filepath + ' ' + destpath
                    cmd = 'mv ' + filepath + ' ' + destpath + ' > nul'
                    os.system(cmd)
                i += 1
            
    
def makeMovies():
    ""
    print 'make mp4 movies using ffmpeg'
    folder = config.moviesFolder
    # print folder
    for root, dirs, files in os.walk(folder):
        # print root, dirs
        # os.chdir(folder)
        if dirs==[]: # reached the leaf level
            print 'directory', root
            savedir = os.getcwd()
            moviefolder = os.path.abspath(root)
            # print moviefolder
            movieName = '_movie.mp4'
            lib.pngsToMp4(moviefolder, filespec, movieName, config.frameRate)
            os.chdir(savedir)


    
def makeLinks():
    "make links from source files (centers or composites or mosaics) to movies folders"
    
    print 'making links from source files'
    
    
    # iterate through all available images
    f = open(config.filesdb, 'rt')
    i = 0
    lastVolume=''
    reader = csv.reader(f)
    for row in reader:
        if i==0:
            fields = row
        else:
            volume = row[config.filesColVolume]
            fileid = row[config.filesColFileId]
            filter = row[config.filesColFilter]

            if volume!=lastVolume:
                print 'volume', volume
                lastVolume = volume
                
            # get subfolder, eg data/step3_centers/VGISS_5101
            # sourceSubfolder = config.centersFolder + '/' + volume
            sourceSubfolder = config.compositesFolder + '/' + volume

            # get source filename and path
            # eg centered_C1327321_RAW_ORANGE.PNG
            # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
            #. make consistent
            # sourcefilename = config.centersprefix + fileid + '_' + config.imageType + '_' + filter + '.PNG' 
            sourcefilename = config.compositesPrefix + fileid + '.PNG' 
            sourcepath = sourceSubfolder + '/' + sourcefilename

            # if file exists, create subfolder and copy/link image
            if os.path.isfile(sourcepath):

                system = row[config.filesColPhase]
                craft = row[config.filesColCraft]
                target = row[config.filesColTarget]
                camera = row[config.filesColInstrument]

                # get subfolder, eg Jupiter/Voyager1/Io/Narrow
                subfolder = system +'/' + craft + '/' + target +'/' + camera 

                # get target file, eg data/step8_movies/jupiter/voyager1/io/narrow/centered....png
                targetfolder = config.moviesFolder + '/' + subfolder
                targetpath = targetfolder + '/' + sourcefilename

                # skip if file already exists (to save time on copying)
                if True:
                # if not os.path.isfile(targetpath):

                    # make sure subfolder exists
                    lib.mkdir_p(targetfolder)

                    # link to file
                    # note: mklink requires admin privileges, so must run this script in an admin console
                    # eg sourcepath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
                    src2 = '../../../../../../' + sourcepath # need to get out of the target dir
                    cmd = 'mklink ' + targetpath + ' ' + src2 + ' > nul'
                    cmd = cmd.replace('/','\\')
                    # print cmd
                    # print 'makelink ' + targetpath
                    os.system(cmd)

        i += 1

    f.close()
    # print
    

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
    # pathSystem, pathCraft, pathTarget, pathCamera = [None,None,None,None]
    
    #. need to remove any existing folders here

    makeLinks()
    renameFilesSequentially()
    makeMovies()

    

if __name__ == '__main__':
    os.chdir('..')
    # buildMovies("Neptune")
    # makeLinks()
    # renameFilesSequentially()
    makeMovies()
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

