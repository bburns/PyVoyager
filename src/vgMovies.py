
# vg movies command
# combine individual clips into one movie using ffmpeg, and add music

# see http://trac.ffmpeg.org/wiki/Concatenate#demuxer


import os
import os.path
import csv

import config
import lib
import libimg


def concatenateClips(movieId, clipIds):
    "Concatenate the given mp4 clips into an mp4 movie"

    print 'Generating movie', movieId
    print movieId, clipIds
    movieFilepath = config.moviesFolder + movieId + '.mp4'
    movieContentsFilepath = config.moviesFolder + movieId + '.txt'
    if clipIds != []:
        makeContentsFile(movieContentsFilepath, clipIds)
        # now make the movie
        # eg "ffmpeg -y -f concat -i Neptune-Voyager2.txt -c copy Neptune-Voyager2.mp4"
        cmd = "ffmpeg -y -f concat -i %s -c copy %s" % (movieContentsFilepath, movieFilepath)
        print cmd
        os.system(cmd)


def makeContentsFile(movieContentsFilepath, clipIds):
    "Make a text file containing a list of mp4 clips that will be merged by ffmpeg"

    f = open(movieContentsFilepath, 'w')
    for clipId in clipIds:
        print clipId
        clipFilepath = config.clipsFolder + clipId + '.mp4'
        movieFilepath = config.moviesFolder + clipId + '.mp4'
        # if file avail, add it
        if os.path.isfile(clipFilepath):
            line = "file '../../" + clipFilepath + "'"
            print >> f, line
        # check in moviesFolder also, so can recurse
        elif os.path.isfile(movieFilepath):
            line = "file '../../" + movieFilepath + "'"
            print >> f, line
    f.close()


def vgMovies():
    "Combine individual clips into movies based on db/movies.csv"

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
                concatenateClips(lastMovieId, clipIds)
                clipIds = []

            clipIds.append(clipId)
            lastMovieId = movieId
        i += 1

    concatenateClips(lastMovieId, clipIds)

    #. then would want to add music, either to each clip, or to all.mp4
    # specify in music.csv


if __name__ == '__main__':
    os.chdir('..')
    vgMovies()
    print 'done'

