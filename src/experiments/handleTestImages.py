
# copy badly centered images to a folder somewhere (desktop/foo)

# then run grabTestImages to gather the original images and add them to the test folder
# then clear the foo folder


import os
import csv

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib


tempFolder = 'c:/users/bburns/desktop/VoyagerTest/'

os.chdir('../..')

#. make getFileInfo(fileId) - return dict of info
def getVolume(fileId):
    "get volume associated with the given file id"
    # slow linear search but ok for this task
    f = open(config.filesdb,'rt')
    reader = csv.reader(f)
    i = 0
    vol = ''
    for row in reader:
        if i==0:
            fields = row
        else:
            if fileId==row[config.filesColFileId]:
                vol = row[config.filesColVolume] # eg 5101
                break
        i+=1
    f.close()            
    return vol





def grabTestImages():
    "for each image in foo folder, grab original (non-centered) image and copy it to the test folder"
    i = 1
    for root, dirs, files in os.walk(tempFolder):
        nfiles = len(files)
        for filename in files:
            # print filename
            ext = filename[-4:]
            if ext=='.png' or ext=='.jpg':
                # print filename # eg C1164724_centered_Clear.png
                if 'centered' in filename:
                    filename = filename.replace('centered','adjusted')
                print filename
                # now what volume did it come from?
                # need to look it up in files.csv
                fileId = filename[:8] # eg C1164724
                print fileId
                vol = getVolume(fileId) # eg 5101
                print vol
                origfolder = config.adjustmentsFolder
                origpath = origfolder + 'VGISS_' + vol + '/' + filename
                print origpath
                # targetpath = testfolder + filename

                # cmd = "cp " + origpath + " " + testfolder
                # cmd = "cp " + origpath + " " + targetpath
                # print cmd
                # os.system(cmd)
                lib.cp(origpath, config.testImagesFolder)

grabTestImages()


# def removeTestImages():
#     "walk through foo folder and for each centered file there, remove the corresponding one from the test folder"
#     i = 1
#     for root, dirs, files in os.walk(tempFolder):
#         nfiles = len(files)
#         for filename in files:
#             # print filename
#             ext = filename[-4:].lower()
#             if ext=='.png' or ext=='.jpg':
#                 origname = filename[9:]
#                 testpath = testfolder + '/' + origname
#                 newpath = testfolder + '/ok/'
#                 cmd = "mv " + testpath + " " + newpath
#                 print cmd
#                 os.system(cmd)
                

# removeTestImages()



