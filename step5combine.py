
# combine individual movies

import os

import config
import lib
import libimg


def make_flight_volume_list(flightnum):
    "build a file containing a list of all the movie files for the given flyby"
    # this is used by ffmpeg to combine the movies into one movie
    flights = config.flights
    # for k,v in flights.iteritems():
    #     print k,v
    vols = flights[flightnum]
    # print vols
    combined_name = 'VGISS_' + str(flightnum)
    movie_path_file = config.combined_folder + '/' + combined_name + '.txt'
    print movie_path_file
    f = open(movie_path_file, 'w')
    for vol in vols:
        voltitle = lib.get_volume_title(vol)
        s = config.movie_folder
        movie_name = voltitle + '.mp4'
        movie_path = s + '/' + voltitle + '/' + movie_name
        # eg file 'C:\Users\bburns\Desktop\DeskDrawer\@voyager\@voyager\data\step4_movies\VGISS_5101\VGISS_5101.mp4'
        line = "file '" + movie_path + "'"
        print line
        print >> f, line
    f.close()

# make_flight_volume_list(51)


def combine_flight(flightnum):
    "combine individual movies into single movie for each flyby"
    make_flight_volume_list(flightnum)
    os.chdir(config.combined_folder)
    flightname = "VGISS_" + str(flightnum)
    flight_volume_list = flightname + '.txt'
    outfile = flightname + ".mp4"
    # eg "ffmpeg -f concat -i VGISS_51.txt -c copy VGISS_51.mp4"
    cmd = "ffmpeg -f concat -i %s -c copy %s" % (flight_volume_list, outfile)
    print cmd
    os.system(cmd)

    
def main():
    combine_flight(51)
    # combine_flight(61)
    # combine_flight(52)
    # combine_flight(62)
    # combine_flight(72)
    # combine_flight(82)
                
if __name__ == '__main__':
    # main()
    pass


