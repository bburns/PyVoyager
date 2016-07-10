
# convert Voyager IMG files to PNG files using img2png


import os.path

import config
import lib

from vgBuildUnzip import buildUnzip


def buildImages(volumeNum):
    "convert IMG files to PNG files, if folder doesn't exist yet"
    print 'build images'
    unzippedpath = lib.getUnzippedpath(volumeNum)
    imagespath = lib.getImagespath(volumeNum)
    filespec = config.imageFilespec # eg "*RAW.IMG"
    if int(volumeNum)==0: # do nothing if asking for test volume
        print 'volume 0 is a test volume, which should be manually created in step3_images/test,'
        print 'and populated with test cases for centering, etc.'
        print
    elif os.path.isdir(imagespath):
        print "Folder exists: " + imagespath
        return False
    else:
        # unzip the download, if not already there
        buildUnzip(volumeNum)
        lib.mkdir(imagespath) # create folder
        datadir = unzippedpath + '/DATA'
        print "converting imgs to pngs for " + datadir
        # for each subdir in datadir, cd subdir, run img2png on all img files in it
        i = 1
        for root, dirs, files in os.walk(datadir):
            ndirs = len(dirs)
            for subdir in dirs:
                dirpath = os.path.join(root, subdir)
                dirpath = os.path.abspath(dirpath)
                print 'dir %d/%d: %s' % (i,ndirs,dirpath)
                lib.img2png(dirpath, filespec, imagespath)
                i += 1
        return True

    
# def buildImage(imageId):
#     "build an image by calling buildImages for the volume associated with the image"
#     #. we'll need a sqlite db with an index for files.txt, or maybe just need this?
#     db = {
#         1385455:5101
#         }
#     #.. or just a table of min values and associated volumes
#     # though there are 50ish volumes, so would be a bit slow to search through.
#     # but could split it into a btree, ie one main 'if' per encounter (6)
#     # if cnum>1380000:
#         # volnum=5101
#     cnum = int(imageId[1:])
#     volnum = db[cnum]
#     buildImages(volnum)
    
#     # open the files.txt db, get the filenum specified and its params,
#     # extract it with img2png if it's not already in the files folder
#     # copy it to the files folder
#     # if step2_unzips doesn't exist, unzip step1_zips
#     # if step1_zips doesn't exist, download it
#     # eg
#     # file6,VGISS_5101,C1462321,Jupiter,Voyager1,Jupiter,Narrow,CLEAR,ISS BEAM BENDING TEST
#     # file7,VGISS_5101,C1462323,Jupiter,Voyager1,Jupiter,Narrow,CLEAR,ISS BEAM BENDING TEST
#     # file8,VGISS_5101,C1462325,Jupiter,Voyager1,Jupiter,Narrow,CLEAR,ISS BEAM BENDING TEST
#     # filedef = getFiledef(fileNum)
#     # volume = filedef['volume']
#     # filetitle = filedef['filetitle']
#     # filetype = 'RAW'
#     # filter = filedef['filter']
#     # imgdir = config.unzipFolder + '/' + volume
#     # pngdir = config.pngFolder + '/' + volume
#     # imgfile = filetitle + '_' + filetype + '.IMG'
#     # pngfile = filetitle + '_' + filetype + '_' + filter + '.PNG'
#     # imgpath = imgdir + '/' + imgfile
#     # pngpath = pngdir + '/' + pngfile
#     # if os.path.isfile(pngpath):
#     #     pass
#     # else:
#     #     lib.img2png(imgdir, imgfile, pngdir):
