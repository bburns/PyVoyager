
"""
vg clear command

Clear folders specified for a given step.
"""

import csv
import os
import os.path

import config
import lib
import libimg



def vgClear(step='', filterVolume=''):

    "clear volume folder for given step"

    filterVolume = str(filterVolume) # eg '5101'
    subfolder = lib.getSubfolder(step, filterVolume)
    print 'Clearing',subfolder
    lib.rmdir(subfolder)
    print

if __name__ == '__main__':
    os.chdir('..')
    print 'done'


