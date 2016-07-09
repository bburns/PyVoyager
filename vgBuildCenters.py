
import os
import os.path

import lib
import libimg
import db
    
from vgBuildImages import buildImages


def buildCenters(volumeNum):
    "build centered images for given volume, if they don't exist yet"
    imagespath = lib.getImagespath(volumeNum)
    centerspath = lib.getCenterspath(volumeNum)
    if volumeNum!=0 and os.path.isdir(centerspath):
        print "Folder exists: " + centerspath
        return False
    else:
        # first build the plain images for the volume, if not already there
        buildImages(volumeNum)
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
    
