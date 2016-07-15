
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


    
def makeLink(targetfolder, sourcepath, nfile, ncopies):
    "make ncopies of symbolic link from the source to the target file, starting with number nfile"
    for i in range(ncopies):
        n = nfile + i
        targetpath2 = targetfolder + config.movieFilespec % n # eg 'img00001.png'
        # eg mklink data\step8_movies\Neptune\Voyager2\Neptune\Narrow\img00001.png ..\..\..\..\..\..\data\step4_centers\VGISS_8208\centered_C1159959_CALIB_Clear.png > nul
        cmd = 'mklink ' + targetpath2 + ' ' + sourcepath + ' > nul'
        cmd = cmd.replace('/','\\')
        os.system(cmd)


def makeLinks(bwOrColor):
    "make links from source files (centers or composites or mosaics) to movies folders"
    
    print 'making links from source files'
    
    centeringInfo = lib.readCsv('db/centering.csv') # get dictionary of dictionaries
    
    nfilesInTargetDir = {}
    
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

            # if file exists, create subfolder and link image
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
                ncopies = 1 if goSlow==False else config.movieFramesForSlowParts

                # get subfolder and make sure it exists
                # eg data/step8_movies/Jupiter/Voyager1/Io/Narrow/
                subfolder = system +'/' + craft + '/' + target +'/' + camera + '/'
                targetfolder = config.moviesFolder + subfolder
                lib.mkdir_p(targetfolder)

                # get current file number in that folder
                nfile = nfilesInTargetDir.get(planetCraftTargetCamera)
                if nfile:
                    pass
                else:
                    nfile = 0
                
                # link to file
                # note: mklink requires admin privileges, so must run this script in an admin console
                # eg pngpath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                pngpathrelative = '../../../../../../' + pngpath # need to get out of the target dir
                makeLink(targetfolder, pngpathrelative, nfile, ncopies)
                
                # increment the file number for the target folder
                nfile += ncopies
                nfilesInTargetDir[planetCraftTargetCamera] = nfile

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
    # renameFilesSequentially()
    makeMovies()
    

if __name__ == '__main__':
    os.chdir('..')
    # buildMovies("Neptune")
    # makeLinks()
    # renameFilesSequentially()
    makeMovies('bw')
    print 'done'

    
