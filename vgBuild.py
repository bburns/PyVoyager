
# build movies, mosaics, composites, centers recursively from source files


import csv
import os
import os.path

import db
import config
import lib
import libimg


from vgBuildDownload import buildDownload
from vgBuildUnzip import buildUnzip
from vgBuildImages import buildImages #, buildImage
from vgBuildCenters import buildCenters #, buildCenter
from vgBuildComposites import buildComposites
from vgBuildTargets import buildTargets
from vgBuildMovies import buildMovies




def buildMosaics():
    "build mosaic images"
    pass



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
    # buildComposites(5101)
    # buildCenter('C1537728')
    # buildCenter('C1537730')
    # buildCenter('C1537732')
    # buildComposite('C1537728')
    # buildItem('foo.movie')
    pass

