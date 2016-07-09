
# ~oo text file database routines

import csv

import lib


#. should pass any constants into functions
import config


def getItem(itemIdOrType, itemNum=''):
    "get set of parameters for the given item"
    # eg getItem('file1') or getItem('file', 1)
    
    itemId = itemIdOrType + str(itemNum)
    itemType, itemNum = lib.splitId(itemId)
    
    # get the db filename
    dbfile = config.dbfolder + itemType + 's.txt' # eg ../data/db/files.txt
    
    # open the db file
    filein = open(dbfile, 'rt')
    i = 0
    item = {}
    try:
        reader = csv.reader(filein)
        for row in reader:
            if i==0:
                fields = row
            else:
                if row[0]==itemId:
                    j = 0
                    for field in fields:
                        item[field] = row[j]
                        j += 1
            i += 1
    finally:
        filein.close()
    
    # return dictionary with item properties
    # eg return {'filename': 'foo.png'}
    return item


def fileGetPath(file):
    "get the path to the given file object"
    volume = file['volume']
    filetitle = file['filetitle']
    filetype = config.filetype
    filter = file['filter']
    filename = filetitle + '_' + filetype + '_' + filter + '.png'
    subdir = volume[:-2] + 'XX'
    path = config.filesFolder + '/' + volume + '/' + filename
    return path


# def unzipGetPath(unzip):
#     "get the path to the given unzip object"
#     volume = file['volume']
#     filetitle = file['filetitle']
#     filter = file['filter']
#     filename = filetitle + '_' + filetype + '_' + filter + '.png'
#     subdir = volume[:-2] + 'XX'
#     path = config.filesFolder + '/' + volume + '/' + subdir + '/' + filename
#     return path



