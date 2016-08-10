
"""
vg grab command

Grabs original (adjusted, uncentered) version of a file stored in the 'grab' folder (./data/grab/),
and puts it in the 'grabbed' folder (./data/grabbed/).
Useful in debugging, centering images manually, etc.
"""

import os
import csv

import lib
import config



#. make getFileInfo(fileId) - return dict of info
def getVolume(fileId):
    "get volume associated with the given file id"
    # slow linear search but ok for this task
    # f = open(config.dbFiles,'rt')
    # reader = csv.reader(f)
    reader, f = lib.openCsvReader(config.dbFiles)
    volume = ''
    for row in reader:
        if fileId==row[config.filesColFileId]:
            volume = row[config.filesColVolume] # eg '5101'
            break
    f.close()
    return volume


def vgGrab():
    """
    for each image in grab folder, grab original (non-centered) image and copy it to the grabbed folder
    """
    i = 1
    for root, dirs, files in os.walk(config.grabFolder):
        nfiles = len(files)
        print root
        for filename in files:
            ext = filename[-4:]
            if ext=='.png' or ext=='.jpg':
                print filename # eg C1164724_centered_Clear.png
                fileId = filename[:8] # eg C1164724
                print fileId
                # now what volume did it come from? need to look it up in files.csv
                volume = getVolume(fileId) # eg 5101
                print volume
                if 'centered' in filename:
                    # filepath = config.centersFolder + 'VGISS_' + volume + '/' + filename
                    filepath = config.folders['center'] + 'VGISS_' + volume + '/' + filename
                    filename = filename.replace('centered','adjusted')
                else:
                    # filepath = config.adjustmentsFolder + 'VGISS_' + volume + '/' + filename
                    filepath = config.folders['adjust'] + 'VGISS_' + volume + '/' + filename
                print filename
                print filepath
                # origpath = config.adjustmentsFolder + 'VGISS_' + volume + '/' + filename
                origpath = config.folders['adjust'] + 'VGISS_' + volume + '/' + filename
                print origpath
                if lib.cp(origpath, config.grabbedFolder):
                    # now remove from grab folder
                    grabpath = config.grabFolder + filename
                    lib.rm(grabpath)


if __name__ == '__main__':
    os.chdir('..')
    vgGrab()
    print 'done'

