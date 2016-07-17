
# build movies associated with target subfolders,
# eg Jupiter/Voyager1/Io/Narrow

# this must be run in an admin console because mklink requires elevated priveleges


#. see also, which remove
# lib.copyFilesSequenced(src, dst, filenamePattern)


import csv
import os
import os.path

import config
import lib

import vgBuildTitles



def makeMovieFiles():
    "build mp4 movies using ffmpeg on sequentially numbered image files"
    print 'make mp4 movies using ffmpeg'
    # folder = config.moviesFolder
    folder = config.moviestageFolder
    # print folder
    for root, dirs, files in os.walk(folder):
        # print root, dirs
        if dirs==[]: # reached the leaf level
            print 'directory', root # eg Neptune/Voyager2/Triton/Narrow
            stageFolder = os.path.abspath(root)
            print stageFolder

            # get target file path relative to staging folder, eg ../../Neptune-Voyager-Triton-Narrow.mp4
            targetPath = root.split('/') # eg ['Neptune','Voyager2',...]
            movieTitle = '-'.join(targetPath) # eg 'Neptune-Voyager2-Triton-Narrow'
            movieTitle = movieTitle + '.mp4'
            moviePath = '../../../../' + moviePath
            print moviePath

            # movieName = '_movie.mp4'
            # lib.pngsToMp4(stageFolder, config.movieFilespec, movieName, config.movieFrameRate)
            lib.pngsToMp4(stageFolder, config.movieFilespec, moviePath, config.movieFrameRate)


def makeLink(targetfolder, sourcepath, nfile, ncopies):
    "make ncopies of symbolic link from the source to the target file, starting with number nfile"
    # this requires running vg from an admin console
    for i in range(ncopies):
        n = nfile + i
        targetpath2 = targetfolder + config.movieFilespec % n # eg 'img00001.png'
        # eg mklink data\step8_movies\Neptune\Voyager2\Neptune\Narrow\img00001.png ..\..\..\..\..\..\data\step4_centers\VGISS_8208\centered_C1159959_CALIB_Clear.png > nul
        cmd = 'mklink ' + targetpath2 + ' ' + sourcepath + ' > nul'
        cmd = cmd.replace('/','\\')
        os.system(cmd)


def makeLinks(bwOrColor, pathparts):
    "make links from source files (centers or composites) to movie stage folders"

    print 'making links from source files'

    # what does the user want to focus on?
    pathSystem, pathCraft, pathTarget, pathCamera = pathparts

    # read some small dbs into memory
    centeringInfo = lib.readCsv('db/centering.csv') # get dictionary of dictionaries
    multitargetInfo = lib.readCsv('db/multitargetImages.csv') # get dictionary of dictionaries

    # keep track of number of files in each target subfolder, so can number files appropriately
    nfilesInTargetDir = {}

    # keep track of which targetpaths we've seen, so know to add titles
    targetpathsSeen = {}

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

                # show progress
                if volume!=lastVolume:
                    print 'volume', volume
                    # print 'volume %s\r' % volume
                    lastVolume = volume

                system = row[config.filesColPhase]
                craft = row[config.filesColCraft]
                target = row[config.filesColTarget]
                camera = row[config.filesColInstrument]

                # relabel target field if necessary - see db/multitargetImages.csv for more info
                targetInfo = multitargetInfo.get(fileId)
                if targetInfo:
                    # make sure old target matches what we have
                    if targetInfo['oldTarget']==target:
                        target = targetInfo['newTarget']

                # is this an image the user wants to see?
                do = True
                if (pathSystem and pathSystem!=system): do = False
                if (pathCraft and pathCraft!=craft): do = False
                if (pathTarget and pathTarget!=target): do = False
                if (pathCamera and pathCamera!=camera): do = False
                if do:

                    # get the centering info, if any, to see if we should slow down here.
                    # info includes planetCraftTargetCamera,centeringOff,centeringOn
                    planetCraftTargetCamera = system + craft + target + camera
                    info = centeringInfo.get(planetCraftTargetCamera)
                    goSlow = False
                    if info:
                        centeringOff = info['centeringOff']
                        centeringOn = info['centeringOn']
                        goSlow = (fileId>=centeringOff) and (fileId<centeringOn)

                    # number of copies of this file to link
                    ncopies = 1 if goSlow==False else config.movieFramesForSlowParts

                    # get staging subfolder and make sure it exists
                    # eg data/step8_movies/Jupiter/Voyager1/Io/Narrow/
                    subfolder = system +'/' + craft + '/' + target +'/' + camera + '/'
                    # targetfolder = config.moviesFolder + subfolder
                    targetfolder = config.moviestageFolder + subfolder
                    lib.mkdir_p(targetfolder)

                    # get current file number in that folder, or start at 0
                    nfile = nfilesInTargetDir.get(planetCraftTargetCamera)
                    if not nfile: nfile = 0

                    # if we haven't seen this subfolder before, add the titlepage image a few times.
                    # titlepages are created in the previous step, vgBuildTitles.
                    seen = targetpathsSeen.get(planetCraftTargetCamera)
                    if not seen:
                        targetpathsSeen[planetCraftTargetCamera] = True
                        titleimagefilepath = config.titlesFolder + subfolder + 'title.png'
                        titleimagepathrelative = '../../../../../../../' + titleimagefilepath # need to get out of the target dir - we're always this deep
                        ntitlecopies = config.movieFramesForTitles
                        makeLink(targetfolder, titleimagepathrelative, nfile, ntitlecopies)
                        nfile += ntitlecopies

                    # link to file
                    # note: mklink requires admin privileges, so must run this script in an admin console
                    # eg pngpath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
                    pngpathrelative = '../../../../../../../' + pngpath # need to get out of the target dir - we're always this deep
                    makeLink(targetfolder, pngpathrelative, nfile, ncopies)

                    # increment the file number for the target folder
                    nfile += ncopies
                    nfilesInTargetDir[planetCraftTargetCamera] = nfile

        i += 1

    f.close()



def buildMovies(bwOrColor, targetPath=None):
    "build bw or color movies associated with the given target path (eg Jupiter/Voyager1/Io/Narrow)"
    # eg buildMovies('bw', 'Jupiter/Voyager1')

    # make sure we have some titles
    vgBuildTitles.buildTitles(targetPath)

    # note: pathparts = [pathSystem, pathCraft, pathTarget, pathCamera]
    pathparts = lib.parseTargetPath(targetPath)

    # remove any existing staged images first
    lib.rmdir(config.moviestageFolder)

    makeLinks(bwOrColor, pathparts)
    makeMovieFiles()


if __name__ == '__main__':
    os.chdir('..')
    print lib.parseTargetPath('')
    # buildMovies('bw', 'Jupiter/Voyager1/Io/Narrow')
    # buildMovies('bw', '//Triton')
    # buildMovies("Neptune")
    # makeLinks()
    print 'done'


