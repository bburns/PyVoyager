
"""
vg grab command
"""


def vgGrab():
    """
    for each image in grab folder, grab original (non-centered) image and copy it to the grabbed folder
    """
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

if __name__ == '__main__':
    os.chdir('..')
    vgGrab()
    print 'done'

