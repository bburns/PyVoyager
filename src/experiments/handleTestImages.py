

# copy badly centered images to a folder somewhere
# then run grabTestImages to gather the original images and add them to the test folder
# then clear the foo folder
# then move well-centered images to foo folder
# then run removeTestImages to remove the corresponding images from the test folder

import os
import csv

import sys; sys.path.append('..') # so can import from main src folder
import config


os.chdir('../..')

tempFolder = 'c:/users/bburns/desktop/foo'
testfolder = config.testFolder


def getVolume(fileId):
    "get volume associated with the given file id"
    f = open(config.filesdb,'rt')
    reader = csv.reader(f)
    i = 0
    vol = ''
    for row in reader:
        if i==0:
            fields = row
        else:
            if fileId==row[config.filesColFileId]:
                vol = row[config.filesColVolume]
                break
        i+=1
    f.close()            
    return vol



def grabTestImages():
    "for each centered image in foo folder, grab original non-centered image and copy it to the test folder"
    i = 1
    for root, dirs, files in os.walk(tempFolder):
        nfiles = len(files)
        for filename in files:
            # print filename
            ext = filename[-4:]
            if ext=='.PNG' or ext=='.png':
                # print filename # eg centered_C1164724_RAW_CLEAR.PNG
                origname = filename[9:]
                print origname
                # now what volume did it come from?
                # need to look it up in files.csv
                fileId = origname[:8]
                print fileId
                vol = getVolume(fileId)
                print vol
                origfolder = config.imagesFolder
                origpath = origfolder + '/' + vol + '/' + origname
                print origpath

                cmd = "cp " + origpath + " " + testfolder
                print cmd
                os.system(cmd)


def removeTestImages():
    "walk through foo folder and for each centered file there, remove the corresponding one from the test folder"
    i = 1
    for root, dirs, files in os.walk(tempFolder):
        nfiles = len(files)
        for filename in files:
            # print filename
            ext = filename[-4:]
            if ext=='.PNG' or ext=='.png':
                origname = filename[9:]
                testpath = testfolder + '/' + origname
                newpath = testfolder + '/ok/'
                cmd = "mv " + testpath + " " + newpath
                print cmd
                os.system(cmd)
                

# grabTestImages()
removeTestImages()



