
# build movies, mosaics, composites, centers recursively from source files


import csv
import os # for system
import os.path

import db
import config
import lib


        
def buildDownload(volumeNum):
    "download the given volume number, if it doesn't exist yet"
    # eg buildZip(5101)
    destfolder = config.downloadFolder
    url = lib.getDownloadUrl(volumeNum) # eg http://.....
    zipfilepath = lib.getZipfilepath(volumeNum) # eg  ../data/step1_downloads/vgiss_5101
    filetitle = url.split('/')[-1] # eg VGISS_5101.tar.gz
    filepath = destfolder + "/" + filetitle
    if os.path.isfile(filepath):
        print "File exists: " + filepath
        return False
    else:
        print "Downloading " + url
        print "         to " + filepath
        return lib.downloadFile(url, filepath)

    
def buildUnzip(volumeNum):
    "unzip the given volume number, if it doesn't exist yet"
    # download the zip if not already there
    buildDownload(volumeNum) 
    zipfilepath = lib.getZipfilepath(volumeNum)
    unzippedpath = lib.getUnzippedpath(volumeNum)
    if os.path.isdir(unzippedpath):
        print "Folder exists: " + unzippedpath
        return False
    else:
        print "Unzipping " + zipfilepath
        print "       to " + unzippedpath
        return lib.unzipFile(zipfilepath, unzippedpath)


# more efficient to build all images in a volume at once    
# filespec = "*" # do all image types
filespec = "*RAW.IMG"

def buildImages(volumeNum):
    "convert IMG files to PNG files, if folder doesn't exist yet"
    print 'build images'
    # unzip the download, if not already there
    buildUnzip(volumeNum)
    unzippedpath = lib.getUnzippedpath(volumeNum)
    imagespath = lib.getImagespath(volumeNum)
    if os.path.isdir(imagespath):
        print "Folder exists: " + imagespath
        return False
    else:
        lib.mkdir(imagespath) # create folder
        datadir = unzippedpath + '/DATA'
        print "converting imgs to pngs for " + datadir
        # for each subdir in datadir, cd subdir, run img2png on all img files in it
        i = 1
        for root, dirs, files in os.walk(datadir):
            nfiles = len(files)
            for subdir in dirs:
                dirpath = os.path.join(root, subdir)
                dirpath = os.path.abspath(dirpath)
                # print 'dir ' + str(i) + ': ' + dirpath
                print 'dir %d/%d: %s' % (i,nfiles,dirpath)
                lib.img2png(dirpath, filespec, imagespath)
                i += 1
        return True

# def buildImage():
    # pass
    # open the files.txt db, get the filenum specified and its params,
    # extract it with img2png if it's not already in the files folder
    # copy it to the files folder
    # if step2_unzips doesn't exist, unzip step1_zips
    # if step1_zips doesn't exist, download it
    # eg
    # file6,VGISS_5101,C1462321,Jupiter,Voyager1,Jupiter,Narrow,CLEAR,ISS BEAM BENDING TEST
    # file7,VGISS_5101,C1462323,Jupiter,Voyager1,Jupiter,Narrow,CLEAR,ISS BEAM BENDING TEST
    # file8,VGISS_5101,C1462325,Jupiter,Voyager1,Jupiter,Narrow,CLEAR,ISS BEAM BENDING TEST
    # filedef = getFiledef(fileNum)
    # volume = filedef['volume']
    # filetitle = filedef['filetitle']
    # filetype = 'RAW'
    # filter = filedef['filter']
    # imgdir = config.unzipFolder + '/' + volume
    # pngdir = config.pngFolder + '/' + volume
    # imgfile = filetitle + '_' + filetype + '.IMG'
    # pngfile = filetitle + '_' + filetype + '_' + filter + '.PNG'
    # imgpath = imgdir + '/' + imgfile
    # pngpath = pngdir + '/' + pngfile
    # if os.path.isfile(pngpath):
    #     pass
    # else:
    #     lib.img2png(imgdir, imgfile, pngdir):
    

def buildCenters(volumeNum):
    "build centered images for given volume, if they don't exist yet"
    # first build the plain images for the volume, if not already there
    buildImages(volumeNum)
    imagespath = lib.getImagespath(volumeNum)
    centerspath = lib.getCenterspath(volumeNum)
    if volumeNum!=0 and os.path.isdir(centerspath):
        print "Folder exists: " + centerspath
        return False
    else:
        lib.mkdir(centerspath) 
        i = 1
        for root, dirs, files in os.walk(imagespath):
            nfiles = len(files)
            for filename in files:
                ext = filename[-4:]
                if ext=='.png':
                    infile = imagespath + '/' + filename
                    outfile = centerspath + '/' + config.centersprefix + filename
                    print 'center %d/%d: %s' %(i,nfiles,infile)
                    libimg.centerImageFile(infile, outfile, config.rotateImage)
                    i += 1
        return True

    
def buildCenter(centerNum):
    "build a centered image, if it doesn't exist yet"
    print 'build center', centerNum
    
    # need to lookup center parameters in centers.txt
    # eg
    # center_id,child_id,x,y
    # center1,file1,120,32
    # center2,file2,321,28
    # center3,file3,188,99
    # eg for center1,
    # you'd load file1 from the files folder,
    # shift it by 120,32
    # save it as center1.png in the centers folder

    # so we want a fn to get the center params
    center = db.getItem('center', centerNum)
    # center = getItem('center'+str(centerNum))
    # which will read the header,
    # find the right row
    # and read the column values into a center object
    # and return it
    # so now we have
    # center = {'child_id': 'file1', 'x':120, 'y': 32}

    # need to look up file1 (or could be composite1, or whatever)
    # and get its params
    fileid = center['child_id']
    file = db.getItem(fileid)
    filepath = db.fileGetPath(file)
    print filepath

    # centerpath = db.centerGetPath(center)
    


def buildComposite(compositeNum):
    "build a composite image by combining channel images"
    # eg
    # C1537728,VGISS_5103,Jupiter,Voyager1,Jupiter,Narrow,BLUE,3 COLOR ROTATION MOVIE
    # C1537730,VGISS_5103,Jupiter,Voyager1,Jupiter,Narrow,ORANGE,3 COLOR ROTATION MOVIE
    # C1537732,VGISS_5103,Jupiter,Voyager1,Jupiter,Narrow,GREEN,3 COLOR ROTATION MOVIE
    # compositeId,childId,filter,weight
    # C1537728.composite,C1537728.center,Blue,1
    # C1537728.composite,C1537730.center,Orange,1
    # C1537728.composite,C1537732.center,Green,1
    pass


def buildMosaic(mosaicNum):
    "build a mosaic image"
    pass


def buildMovie(movieId):
    "build a movie"

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
    # tests
    # buildDownload(5108)
    
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
    
    buildItem('foo.movie')
    
    pass

