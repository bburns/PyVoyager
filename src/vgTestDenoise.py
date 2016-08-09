
"""
vg test denoise command

Test of denoising routines.
Any experimenting with settings should be done in libimg or config settings.
"""

import cv2
import os

import config
import lib
import libimg


def vgTestDenoise():

    print 'Running denoising tests...'
    
    denoisedFolder = config.testDenoiseImagesFolder + 'denoised/'

    lib.rmdir(denoisedFolder)
    lib.mkdir(denoisedFolder)
    # os.mkdir(denoisedFolder)

    for root, dirs, files in os.walk(config.testDenoiseImagesFolder): # test/denoise
        for filename in files:
            ext = filename[-4:].lower()
            if ext=='.jpg' or ext=='.png':
                fileId = filename[:8] # eg C1328423
                fileTitle = filename[:-4] # eg C1328423_neptune_dim
                infile = config.testDenoiseImagesFolder + filename
                denoisedFile = denoisedFolder + filename
                
                print 'denoising', filename
                libimg.denoiseImageFile(infile, denoisedFile)
                
        del dirs[:] # don't recurse
    print 'done'


if __name__ == '__main__':
    os.chdir('..')
    vgTestCenter()
    # print 'done'

