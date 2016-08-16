
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
    
    testDenoiseImagesFolder = config.testFolder + 'denoise/'
    # denoisedFolder = config.testDenoiseImagesFolder + 'denoised/'
    # lib.rmdir(denoisedFolder)
    # lib.mkdir(denoisedFolder)
    # os.mkdir(denoisedFolder)
    folder = testDenoiseImagesFolder

    for root, dirs, files in os.walk(testDenoiseImagesFolder): # test/denoise
        for filename in files: # eg C1328423_neptune_dim.jpg
            ext = filename[-4:].lower()
            if (ext=='.jpg' or ext=='.png') and (not 'denoised' in filename):
                fileId = filename[:8] # eg C1328423
                fileTitle = filename[:-4] # eg C1328423_neptune_dim
                infile = folder + filename
                outfile = folder + fileTitle + '_denoised.jpg'
                
                print 'Denoising', filename
                libimg.denoiseImageFile(infile, outfile)
                
                
        del dirs[:] # don't recurse
    print 'done'


if __name__ == '__main__':
    os.chdir('..')
    vgTestCenter()
    # print 'done'

