
# build movies, mosaics, composites, centers recursively from source files


import csv
import os # for system
import os.path

import db
import config
import lib
import libimg


from vgBuildDownload import buildDownload
from vgBuildUnzip import buildUnzip
from vgBuildImages import buildImages, buildImage
from vgBuildCenters import buildCenters, buildCenter

        


def buildComposite(compositeNum):
    "build a composite image by combining channel images"
    # eg
    # composites: 
    # compositeId,childId,filter,weight
    # C1537728.composite,C1537728.center,Blue,1
    # C1537728.composite,C1537730.center,Orange,1
    # C1537728.composite,C1537732.center,Green,1
    # files:
    # C1537728,VGISS_5103,Jupiter,Voyager1,Jupiter,Narrow,BLUE,3 COLOR ROTATION MOVIE
    # C1537730,VGISS_5103,Jupiter,Voyager1,Jupiter,Narrow,ORANGE,3 COLOR ROTATION MOVIE
    # C1537732,VGISS_5103,Jupiter,Voyager1,Jupiter,Narrow,GREEN,3 COLOR ROTATION MOVIE
    pass


def buildMosaic(mosaicNum):
    "build a mosaic image"
    # eg
    pass



def buildTarget(targetPath):
    "link images to correct subfolders (eg Jupiter/Voyager1/Io/Narrow)"
    
    # iterate down files.txt
    # if target path matches row,
    # copy that image to new subfolder
    
    # voltitle = lib.getVolumeTitle(volnumber)
    # centersfolder = config.centersFolder + '/' + voltitle
    
    #. assume these are all None for now
    # [system, craft, target, camera] = targetPath.split('/')
    
    f = open(config.indexfile, 'rt')
    try:
        reader = csv.reader(f)
        for row in reader:
            filename = row[config.colFilename].strip()
            ext = filename.split('.')[1]
            
            # get field values
            craft = row[config.colCraft].strip()
            phase = row[config.colPhase].strip()
            target = row[config.colTarget].strip()
            instrument = row[config.colInstrument].strip()
            filter = row[config.colFilter].strip()

            # translate field values
            craft = config.translations[craft]
            phase = config.translations[phase]
            target = target.title()
            instrument = config.translations[instrument]
            
            # get source filename
            # eg centered_foo_ORANGE.PNG
            filename = 'centered_' + filename.split('.')[0] + '_' + filter + '.PNG' 
            src = centersfolder + '/' + filename
            
            # if file exists, create subfolder and copy/link image
            if os.path.isfile(src):

                # create subfolder
                # eg Jupiter/Voyager1/Io/Narrow
                subfolder = config.targetFolder + '/' + phase +'/' + craft + '/' + target +'/' + instrument 
                lib.mkdir_p(subfolder)

                # copy file
                # cp -s, --symbolic-link - make symbolic links instead of copying [but is ignored on windows]
                #. mklink requires admin privileges - handle later
                cmd = 'cp ' + src + ' ' + subfolder
                print cmd
                os.system(cmd)
                
    finally:
        f.close()
    




def buildMovie(movieId):
    "build a movie"
    # eg

    print 'build movie'
    
    # need to lookup the contents of the movie in the movies.txt db
    # for each frame, call buildItem, which will dispatch on the item type and recurse
    # then at the end of the list, stage the images and run ffmpeg on them
    
    filenamePattern = 'img%04d.png'
    
    # so need to open movies.txt, scan through rows till find movieId,
    # gather all child_ids and params
    # call buildItem with the id and params
    filein = open(config.moviesdb, 'rt')
    i = 0
    try:
        reader = csv.reader(filein)
        for row in reader:
            if i==0:
                pass
            else:
                movieId = row[0]
                # if movieId==
                childId = row[1]
                buildItem(childId)
                #. copy item to sequential staging folder
                print 'copy item', filenamePattern % i
                i += 1
    finally:
        filein.close()
    
    # need to stage all the files first, numbering them sequentially
    # copy them to a folder like step4_movies/movie1/
    # will need to do individually, as each image could be located in a different folder
    
    # voltitle = lib.getVolumeTitle(volnum) # eg VGISS_5101
    # src = config.centersFolder + '/' + voltitle
    # dst = config.moviesFolder + '/' + voltitle
    
    # # stage files for ffmpeg
    # filenamePattern = 'img%04d.png'
    # lib.copyFilesSequenced(src, dst, filenamePattern)
    
    # # now make movie with ffmpeg
    # movieName = '_' + voltitle + '.mp4' # prepend _ so sorts at start of file list
    # lib.pngsToMp4(dst, filenamePattern, movieName, config.frameRate)



def buildItem(itemId):
    "build an item with the given id - can be a movie, mosaic, composite, center, etc"
    # eg buildItem('movie15')
    
    # extract type and numeric id
    itemType, itemNum = lib.splitId(itemId)
    
    # dispatch on item type
    if itemType=='movie':
        # buildMovie(itemNum)
        buildMovie(itemId)
    elif itemType=='center':
        buildCenter(itemNum)
    elif itemType=='composite':
        buildComposite(itemNum)
    elif itemType=='file':
        buildFile(itemNum)


if __name__ == '__main__':
    
    buildTarget()
    
    # buildImage('C1385455')
    
    # buildDownload(8202)
    
    # print getItem('file2')
    # buildItem('movie1')
    # buildItem('center1')
    # buildItem('C1537728_center')

    # buildCenters(5108)
    
    # ? 
    # buildComposites(5101)
    
    # buildCenter('C1537728')
    # buildCenter('C1537730')
    # buildCenter('C1537732')
    # buildComposite('C1537728')
    
    # buildItem('foo.movie')
    
    pass

