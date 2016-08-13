
"""
vg movies command

Combine individual clips into one movie using ffmpeg, and add music.

See http://trac.ffmpeg.org/wiki/Concatenate#demuxer
"""

import os
import os.path
import csv

import config
import lib
import libimg


def makeContentsFile(movieContentsFilepath, clipIds):
    "Make a text file containing a list of mp4 clips that will be merged by ffmpeg"

    f = open(movieContentsFilepath, 'w')
    for clipId in clipIds:
        print clipId
        clipFilepath = config.folders['clips'] + clipId + '.mp4'
        movieFilepath = config.folders['movies'] + clipId + '.mp4'
        # if file avail, add it
        if os.path.isfile(clipFilepath):
            line = "file '../../" + clipFilepath + "'"
            print >> f, line
        # check in moviesFolder also, so can recurse
        elif os.path.isfile(movieFilepath):
            line = "file '../../" + movieFilepath + "'"
            print >> f, line
    f.close()


def concatenateClips(movieId, clipIds):
    "Concatenate the given mp4 clips into an mp4 movie"

    print 'Generating movie', movieId
    print movieId, clipIds
    movieFilepath = config.folders['movies'] + movieId + '.mp4'
    movieContentsFilepath = config.folders['movies'] + movieId + '.txt'
    if clipIds != []:
        makeContentsFile(movieContentsFilepath, clipIds)
        # now make the movie
        # eg "ffmpeg -y -f concat -i Neptune-Voyager2.txt -c copy Neptune-Voyager2.mp4"
        cmd = "ffmpeg -y -f concat -i %s -c copy %s" % (movieContentsFilepath, movieFilepath)
        print cmd
        os.system(cmd)


def vgMovies():
    """
    Combine individual clips into movies based on db/movies.csv

    walk over db/movies.csv file, eg
    movieId,clipId
    Jupiter-Voyager1,Jupiter-Voyager1-Title
    Jupiter-Voyager1,Jupiter-Voyager1-Jupiter-Narrow
    Jupiter-Voyager1,Jupiter-Voyager1-Io-Narrow
    Jupiter-Voyager1,Jupiter-Voyager1-Europa-Narrow

    """

    # get new movieId,
    # get clipId if available
    # check for clips in clips folder and movies folder, since recurses to build all.mp4
    # add clipId.mp4 to movieId.txt
    # if no clips available then skip movie
    # build the movie mp4 using ffmpeg and the movieId.txt listing
    # repeat until eof
    # should end up with movies for each planet flyby, and one with all of them, all.mp4

    csvMovies, fMovies = lib.openCsvReader(config.dbMovies)
    lastMovieId = ''
    clipIds = []
    for row in csvMovies:
        movieId = row[0] # eg Neptune-Voyager2
        clipId = row[1] # eg Neptune-Voyager2-Triton-Narrow
        if movieId != lastMovieId and lastMovieId != '':
            concatenateClips(lastMovieId, clipIds)
            clipIds = []
        clipIds.append(clipId)
        lastMovieId = movieId

    concatenateClips(lastMovieId, clipIds)
    fMovies.close()

    # then would want to add music to all.mp4, or per system clip
    # specify in music.csv?
    # make vg music step?
    # eg
    # Jupiter-Voyager1,music/foo.mp3
    # Saturn-Voyager1,music/bar.mp3
    # or
    # All,music/baz.mp3




if __name__ == '__main__':
    os.chdir('..')
    vgMovies()
    print 'done'

