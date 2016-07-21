
# vg retarget command
# to use this, browse through images produced by vg targets,
# check for images that are misfiled,
# move them to a temp folder (specified below),
# then run this command, which will print out records to add to targets.csv
# add those records
# then delete the files from the temp folder
# next time clips are built the images will be retargeted to the appropriate subfolder and clip


import os


tempFolder = 'c:/users/bburns/desktop/foo'


def retarget(oldTarget, newTarget):
    "for each image in temp directory, print a retargeting record to be added to targets.csv"
    print 'imageId,oldTarget,newTarget,x,y'
    for root, dirs, files in os.walk(tempFolder):
        nfiles = len(files)
        for filename in files:
            ext = filename[-4:]
            if ext=='.png':
                # origname = filename[9:] # eg C1164724_RAW_Clear.png
                # fileId = origname[:8] # eg C1164724
                fileId = filename[:8] # eg C1164724
                # C0903842,Triton,Neptune
                print '%s,%s,%s' % (fileId, oldTarget, newTarget)


# retarget('Uranus', 'SomeMoon')



