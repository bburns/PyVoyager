
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
            lib.pngsToMp4(moviefolder, config.movieFilespec, movieName, config.movieFrameRate)
            os.chdir(savedir)


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
            
    
#. could speed up if you kept track of nfiles per target folder, in a dictionary
# ie skip the renaming step
def makeLink(targetpath, sourcepath, ncopies):
    "make ncopies of symbolic link from the source to the target file"
    for i in range(ncopies):
        targetpath2 = targetpath[:-4] + str(i) + targetpath[-4:]
        # eg mklink data\step8_movies\Neptune\Voyager2\Neptune\Narrow\centered_C1159959_CALIB_Clear0.png ..\..\..\..\..\..\data\step4_centers\VGISS_8208\centered_C1159959_CALIB_Clear.png > nul
        cmd = 'mklink ' + targetpath2 + ' ' + sourcepath + ' > nul'
        cmd = cmd.replace('/','\\')
        # print cmd
        os.system(cmd)


def makeLinks(bwOrColor):
    "make links from source files (centers or composites or mosaics) to movies folders"
    
    print 'making links from source files'
    
    centeringInfo = lib.readCsv('db/centering.csv') # get dictionary of dictionaries
    
    # nfilesInTargetDir = {}
    
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
            fileId = row[config.filesColFileId]
            filter = row[config.filesColFilter]

            if volume!=lastVolume:
                print 'volume', volume
                lastVolume = volume
                
            # get sourcepath
            # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
            if bwOrColor=='bw':
                pngSubfolder = config.centersFolder + 'VGISS_' + volume + '/'
                pngfilename = config.centersPrefix + fileId + '_' + config.imageType + '_' + filter + '.png' 
            else:
                pngSubfolder = config.compositesFolder + 'VGISS_' + volume + '/'
                pngfilename = config.compositesPrefix + fileId + '.png' 
            pngpath = pngSubfolder + pngfilename

            # if file exists, create subfolder and copy/link image
            if os.path.isfile(pngpath):

                system = row[config.filesColPhase]
                craft = row[config.filesColCraft]
                target = row[config.filesColTarget]
                camera = row[config.filesColInstrument]
                
                # get the centering info, if any, to see if we should slow down here.
                # info includes planetCraftTargetCamera,centeringOff,centeringOn
                planetCraftTargetCamera = system + craft + target + camera
                info = centeringInfo.get(planetCraftTargetCamera)
                goSlow = False
                if info:
                    centeringOff = info['centeringOff']
                    centeringOn = info['centeringOn']
                    goSlow = fileId>=centeringOff and fileId<centeringOn
                ncopies = 1 if goSlow==False else config.moviesFramesForSlowParts

                # get subfolder and target file
                # eg data/step8_movies/Jupiter/Voyager1/Io/Narrow/centered_C1327321_RAW_Orange.png
                subfolder = system +'/' + craft + '/' + target +'/' + camera + '/'
                targetfolder = config.moviesFolder + subfolder
                targetpath = targetfolder + pngfilename

                # make sure subfolder exists
                lib.mkdir_p(targetfolder)

                # nfile = nfilesInTargetDir.get(planetCraftTargetCamera)
                
                # link to file
                # note: mklink requires admin privileges, so must run this script in an admin console
                # eg pngpath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                pngpathrelative = '../../../../../../' + pngpath # need to get out of the target dir
                makeLink(targetpath, pngpathrelative, ncopies)

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
    
    #. need to remove any existing folders

    makeLinks(bwOrColor)
    renameFilesSequentially()
    makeMovies()
    

if __name__ == '__main__':
    os.chdir('..')
    # buildMovies("Neptune")
    # makeLinks()
    # renameFilesSequentially()
    makeMovies('bw')
    print 'done'

    
