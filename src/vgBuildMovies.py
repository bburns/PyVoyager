
# vg movies command
# combine individual clips into one movie using ffmpeg, and add music

# see http://trac.ffmpeg.org/wiki/Concatenate#demuxer


import os
import os.path
import csv

import config
import lib
import libimg


def handleMovie(movieId, clipIds):
    ""
    print movieId, clipIds
    movieFilepath = config.moviesFolder + movieId + '.mp4'
    movieContentsFilepath = config.moviesFolder + movieId + '.txt'
    makeContentsFile(movieContentsFilepath, clipIds)
    # now make the movie
    # os.chdir(config.moviesFolder)
    # flightname = "VGISS_" + str(flightnum)
    # flightVolumeList = flightname + '.txt'
    # outfile = flightname + ".mp4"
    # eg "ffmpeg -f concat -i VGISS_51.txt -c copy VGISS_51.mp4"
    # eg "ffmpeg -f concat -i Neptune-Voyager2.txt -c copy Neptune-Voyager2.mp4"
    cmd = "ffmpeg -f concat -i %s -c copy %s" % (movieContentsFilepath, movieFilepath)
    print cmd
    os.system(cmd)


def makeContentsFile(movieContentsFilepath, clipIds):
    "make a text file containing a list of mp4 clips that will be merged by ffmpeg"
    f = open(movieContentsFilepath, 'w')
    for clipId in clipIds:
        clipFilepath = config.clipsFolder + clipId + '.mp4'
        movieFilepath = config.moviesFolder + clipId + '.mp4'
        # if file avail, add it
        if os.path.isfile(clipFilepath):
            line = "file '" + clipFilepath + "'"
            print >> f, line
        # check in moviesFolder also, so can recurse
        elif os.path.isfile(movieFilepath):
            line = "file '" + movieFilepath + "'"
            print >> f, line
    f.close()


# def makeFlightVolumeList(flightnum):
#     "build a file containing a list of all the movie files for the given flyby"
#     # this is used by ffmpeg to combine the movies into one movie
#     flights = config.flights
#     vols = flights[flightnum]
#     combinedName = 'VGISS_' + str(flightnum)
#     moviePathFile = config.movieFolder + '/' + combinedName + '.txt'
#     print moviePathFile
#     f = open(moviePathFile, 'w')
#     for vol in vols:
#         voltitle = lib.getVolumeTitle(vol)
#         s = config.movieFolder
#         movieName = '_' + voltitle + '.mp4' # prepend _ so will sort at beginning of file list
#         moviePath = s + '/' + voltitle + '/' + movieName
#         # eg file 'C:\Users\bburns\Desktop\DeskDrawer\@voyager\@voyager\data\step4_movies\VGISS_5101\_VGISS_5101.mp4'
#         line = "file '" + moviePath + "'"
#         print line
#         print >> f, line
#     f.close()


def buildMovies():
    "combine individual clips into movies based on db/movies.csv"
    # makeClipList()

    # walk over db/movies.csv file, eg
    # movieId,clipId
    # Jupiter-Voyager1,Jupiter-Voyager1-Title
    # Jupiter-Voyager1,Jupiter-Voyager1-Jupiter-Narrow-Color
    # Jupiter-Voyager1,Jupiter-Voyager1-Io-Narrow-Color
    # Jupiter-Voyager1,Jupiter-Voyager1-Europa-Narrow-Color

    # get new movieId,
    # get clipId if available
    # check for clips in clips folder and movies folder, since recurses to build all.mp4
    # add clipId.mp4 to movieId.txt
    # if no clips available then skip movie
    # build the movie mp4 using ffmpeg and the movieId.txt listing
    # repeat until eof
    # should end up with movies for each planet flyby, and one with all of them, all.mp4

    f = open(config.moviesdb, 'rt')
    reader = csv.reader(f)
    i = 0
    lastMovieId=''
    clipIds = []
    for row in reader:
        if row==[] or row[0][0]=="#": continue # ignore blank lines and comments
        if i==0: fields = row
        else:
            movieId = row[0] # eg Neptune-Voyager2
            clipId = row[1] # eg Neptune-Voyager2-Triton-Narrow
            if movieId != lastMovieId and lastMovieId != '':
                handleMovie(lastMovieId, clipIds)
                clipIds = []

            clipIds.append(clipId)
            lastMovieId = movieId
        i += 1

    handleMovie(lastMovieId, clipIds)


    #. then would want to add music, either to each clip, or to all.mp4
    # specify in music.csv

    # os.chdir(config.moviesFolder)
    # flightname = "VGISS_" + str(flightnum)
    # flightVolumeList = flightname + '.txt'
    # outfile = flightname + ".mp4"
    # eg "ffmpeg -f concat -i VGISS_51.txt -c copy VGISS_51.mp4"
    # cmd = "ffmpeg -f concat -i %s -c copy %s" % (flightVolumeList, outfile)
    # print cmd
    # os.system(cmd)


if __name__ == '__main__':
    os.chdir('..')
    buildMovies()
    print 'done'



