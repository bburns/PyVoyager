
# rename files
# used when changed filename scheme from adjusted_...Clear.png to ..._adjusted_Clear.png, etc
# 2016-07-26


import os


import sys; sys.path.append('..') # so can import from main src folder
import config



# for root, dirs, files in os.walk('../../data/step04_adjustments/'):
#     print root
#     for filename in files:
#         # print filename # eg C1385455_CALIB_Clear_adjusted.png
#         imageId = filename[:8]
#         filter = filename[15:-13]
#         newfilename = imageId + '_adjusted_' + filter + '.png'
#         # print newfilename
#         filepath = root + '/' + filename
#         newfilepath = root + '/' + newfilename
#         os.rename(filepath, newfilepath)

for root, dirs, files in os.walk('../../data/step05_centers/'):
    print root
    for filename in files:
        if 'centered.png' in filename:
            # print filename # eg C1385455_CALIB_Clear_centered.png
            imageId = filename[:8]
            filter = filename[15:-13]
            newfilename = imageId + '_centered_' + filter + '.png'
            # print newfilename
            filepath = root + '/' + filename
            newfilepath = root + '/' + newfilename
            os.rename(filepath, newfilepath)

# for root, dirs, files in os.walk('../../data/step06_composites/'):
#     print root
#     for filename in files:
#         # print filename
#         if filename[:10]=='composite_':
#             newfilename = filename[10:-4] + '_composite.png'
#             filepath = root + '/' + filename
#             newfilepath = root + '/' + newfilename
#             cmd = "mv " + filepath + " " + newfilepath
#             # print cmd
#             os.system(cmd)
#     print

os.system('beep')
