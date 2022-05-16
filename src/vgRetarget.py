"""
vg retarget command

to use this, browse through images produced by vg targets,
check for images that are misfiled,
move them to grab folder
then run this command, which will print out records to add to targets.csv
add those records
then delete the files from the grab folder
next time clips are built the images will be retargeted to the appropriate subfolder and clip
"""

import os

import config


def vgRetarget(oldTarget, newTarget):

    "for each image in temp directory, print a retargeting record to be added to targets.csv"

    print 'imageId,oldTarget,newTarget,x,y'
    # folder = config.grabFolder
    # folder = config.folders['grab']
    for root, dirs, files in os.walk(config.grabFolder):
        nfiles = len(files)
        for filename in files:
            ext = filename[-4:]
            if ext=='.png' or ext=='.jpg':
                fileId = filename[:8] # eg C1164724
                # eg C0903842,Triton,Neptune
                print '%s,%s,%s' % (fileId, oldTarget, newTarget)


# retarget('Uranus', 'SomeMoon')



