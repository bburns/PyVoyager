
# combine individual movies

import os

import config
import lib
import libimg


def makeFlightVolumeList(flightnum):
    "build a file containing a list of all the movie files for the given flyby"
    # this is used by ffmpeg to combine the movies into one movie
    flights = config.flights
    # for k,v in flights.iteritems():
    #     print k,v
    vols = flights[flightnum]
    # print vols
    combinedName = 'VGISS_' + str(flightnum)
    moviePathFile = config.combinedFolder + '/' + combinedName + '.txt'
    print moviePathFile
    f = open(moviePathFile, 'w')
    for vol in vols:
        voltitle = lib.getVolumeTitle(vol)
        s = config.movieFolder
        movieName = voltitle + '.mp4'
        moviePath = s + '/' + voltitle + '/' + movieName
        # eg file 'C:\Users\bburns\Desktop\DeskDrawer\@voyager\@voyager\data\step4_movies\VGISS_5101\VGISS_5101.mp4'
        line = "file '" + moviePath + "'"
        print line
        print >> f, line
    f.close()


def combineFlight(flightnum):
    "combine individual movies into single movie for each flyby"
    makeFlightVolumeList(flightnum)
    os.chdir(config.combinedFolder)
    flightname = "VGISS_" + str(flightnum)
    flightVolumeList = flightname + '.txt'
    outfile = flightname + ".mp4"
    # eg "ffmpeg -f concat -i VGISS_51.txt -c copy VGISS_51.mp4"
    cmd = "ffmpeg -f concat -i %s -c copy %s" % (flightVolumeList, outfile)
    print cmd
    os.system(cmd)

    
def main():
    combineFlight(51)
    # combineFlight(61)
    # combineFlight(52)
    # combineFlight(62)
    # combineFlight(72)
    # combineFlight(82)
                
if __name__ == '__main__':
    # main()
    pass


