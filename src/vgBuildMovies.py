
# build movies associated with target subfolders,
# eg Jupiter/Voyager1/Io/Narrow

# this must be run in an admin console


#. see also, which remove
# lib.copyFilesSequenced(src, dst, filenamePattern)


import csv
import os
import os.path

import config
import lib


def renameFilesSequentially():
    "rename all files in the movie folders so they are numbered sequentially for ffmpeg to use"
    # eg img00001.png, img00002.png, etc
    
    print 'rename files sequentially'
    
    # for each subdir in datadir, cd subdir, run img2png on all img files in it
    folder = config.moviesFolder
    for root, dirs, files in os.walk(folder):
        # print root, dirs
        if dirs==[]: # reached the leaf level
            print root
            i = 1
            for filename in files:
                dest = config.movieFilespec % i  # eg 'img00001.png'
                filepath = root + '\\' + filename
                destpath = root + '\\' + dest
                cmd = 'mv ' + filepath + ' ' + destpath + ' > nul'
                os.system(cmd)
                i += 1
            
    
def makeMovies():
    "build mp4 movies using ffmpeg on sequentially numbered image files"
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
            lib.pngsToMp4(moviefolder, config.movieFilespec, movieName, config.frameRate)
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
        if row==[] or row[0][0]=="#":
            pass
        elif i==0:
            fields = row
        else:
            volume = row[config.filesColVolume]
            fileid = row[config.filesColFileId]
            filter = row[config.filesColFilter]

            if volume!=lastVolume:
                print 'volume', volume
                lastVolume = volume
                
            #.. switch source here - bw or color - pass as required option
            # get subfolder, eg data/step3_centers/VGISS_5101
            sourceSubfolder = config.centersFolder + 'VGISS_' + volume + '/'
            # sourceSubfolder = config.compositesFolder + 'VGISS_' + volume + '/'

            # get source filename and path
            # eg centered_C1327321_RAW_ORANGE.PNG
            # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_ORANGE.PNG
            #. make consistent
            sourcefilename = config.centersPrefix + fileid + '_' + config.imageType + '_' + filter + '.png' 
            # sourcefilename = config.compositesPrefix + fileid + '.png' 
            sourcepath = sourceSubfolder + sourcefilename

            # if file exists, create subfolder and copy/link image
            if os.path.isfile(sourcepath):

                system = row[config.filesColPhase]
                craft = row[config.filesColCraft]
                target = row[config.filesColTarget]
                camera = row[config.filesColInstrument]

                # get subfolder, eg Jupiter/Voyager1/Io/Narrow/
                subfolder = system +'/' + craft + '/' + target +'/' + camera + '/'

                # get target file, eg data/step8_movies/jupiter/voyager1/io/narrow/centered....png
                targetfolder = config.moviesFolder + subfolder
                targetpath = targetfolder + sourcefilename

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
    

# def buildMovies(targetPath):
def buildMovies(bwOrColor):
    "build movies associated with the given target path (eg Jupiter/Voyager1/Io/Narrow)"
    # eg buildMovies("Jupiter")

    #. for now say they're all on
    # parts = targetPath.split('/')
    # while len(parts)<4:
        # parts.append(None)
    # print parts
    # pathSystem, pathCraft, pathTarget, pathCamera = parts
    # pathSystem, pathCraft, pathTarget, pathCamera = [None,None,None,None]
    
    #. need to remove any existing folders here

    # makeLinks()
    # renameFilesSequentially()
    # makeMovies()
    

if __name__ == '__main__':
    os.chdir('..')
    # buildMovies("Neptune")
    # makeLinks()
    # renameFilesSequentially()
    makeMovies()
    print 'done'

    
    
    
    
