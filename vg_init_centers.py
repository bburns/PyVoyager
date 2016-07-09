
# build centers.txt file by attempting to center images in files.txt 

import os

import config
import lib
import libimg


# prefix = 'centered_'

# def centerVolume(volnumber):
#     "center all the images in the given volume"
#     pngpath = lib.getPngpath(volnumber)
#     centeredpath = lib.getCenteredpath(volnumber)
#     if volnumber!=0 and os.path.isdir(centeredpath):
#         print "Folder exists: " + pngpath
#         return False
#     else:
#         try:
#             os.mkdir(centeredpath) 
#         except:
#             pass
#         i = 0
#         for root, dirs, files in os.walk(pngpath):
#             for filename in files:
#                 ext = filename[-4:]
#                 if ext=='.png':
#                     infile = pngpath + '/' + filename
#                     outfile = centeredpath + '/' + prefix + filename
#                     print 'file ' + str(i) + ': ' + infile
#                     libimg.centerImageFile(infile, outfile, config.rotateImage)
#                     i += 1
#         return True


# def main():
    
#     # test volume
#     # centerVolume(0)
    
#     # center a certain number of volumes
#     n = config.nvolumesToCenter
#     for volume in config.volumes:
#         if n>0:
#             if centerVolume(volume):
#                 n -= 1
                
# if __name__ == '__main__':
#     main()


