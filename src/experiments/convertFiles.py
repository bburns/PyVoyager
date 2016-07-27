

# used for converting pngs to jpgs
# 2016-07-26


import os

import sys; sys.path.append('..') # so can import from main src folder
import config


for root, dirs, files in os.walk('../../data/step04_adjustments/'):
# for root, dirs, files in os.walk('../../data/step05_centers/'):
# for root, dirs, files in os.walk('../../data/step06_composites/'):
    print root
    curdir = os.getcwd()
    os.chdir(root)
    cmd = "mogrify -format jpg *.png"
    # cmd = "rm *.png"
    # print cmd
    os.system(cmd)
    os.chdir(curdir)

# os.system('beep')


