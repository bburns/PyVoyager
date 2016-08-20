
"""
vg clear command

Remove folders specified for a given step.
This is needed because the -y option sometimes fails to delete a folder
if Windows still has a lock on it, eg thumbs.db.
Better to have it fail up front with this cmd if going to leave a long cmd running. 
"""

import csv
import os
import os.path

import config
import lib
import libimg



def vgClear(step='', filterVolume=''):

    "remove volume folder for given step"

    filterVolume = str(filterVolume) # eg '5101'
    subfolder = lib.getSubfolder(step, filterVolume)
    print 'Clearing',subfolder
    lib.rmdir(subfolder)
    # print

if __name__ == '__main__':
    os.chdir('..')
    print 'done'


