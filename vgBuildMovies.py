
# build movies associated with target subfolders,
# eg Jupiter/Voyager1/Io/Narrow


import csv

import config
import lib



def buildMovies(targetPath):
    "build movies associated with the given target path (eg Jupiter/Voyager1/Io/Narrow)"

    # this will be similar to buildtargets, but make links instead of copying files
    # and number them sequentially also
    
    pass




    
    
    
    
    
    
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
