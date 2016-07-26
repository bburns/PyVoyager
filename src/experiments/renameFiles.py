
import os


import sys; sys.path.append('..') # so can import from main src folder
import config



for root, dirs, files in os.walk('../../data/step04_adjustments/'):
    print root
    for filename in files:
        # print filename
        if filename[:9]=='adjusted_':
            newfilename = filename[9:-4] + '_adjusted.png'
            filepath = root + '/' + filename
            newfilepath = root + '/' + newfilename
            cmd = "mv " + filepath + " " + newfilepath
            # print cmd
            os.system(cmd)
    print

for root, dirs, files in os.walk('../../data/step05_centers/'):
    print root
    for filename in files:
        # print filename
        if filename[:9]=='centered_':
            newfilename = filename[9:-4] + '_centered.png'
            filepath = root + '/' + filename
            newfilepath = root + '/' + newfilename
            cmd = "mv " + filepath + " " + newfilepath
            # print cmd
            os.system(cmd)
    print

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

