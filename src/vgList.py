
"""
vg list command

Show listing of volumes and what stage they're at.
"""

import os
import tabulate

import config


def parseFilenames(folder, section, grid):
    "parse dir+filenames in the given folder, add x to grid dictionary for volumes present"
    for root, dirnames, filenames in os.walk(folder):
        itemnames = dirnames
        itemnames.extend(filenames)
        for itemname in itemnames: # eg VGISS_5101.tar.gz
            if itemname[:6]=='VGISS_':
                volnum = itemname[6:10] # eg 5101
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Volume'] = volnum
                grid[volnum][section] = 'x'
        del dirnames[:] # don't recurse


# def vgList(volnums=None, imageIds=None, targetPath=None):
def vgList(filterVolumes=''):

    "Get a listing of volumes and what stages they are at"

    headers = ['Volume', 'Download', 'Unzip', 'Convert', 'Adjust',
               'Denoise', 'Center', 'Composite', 'Mosaic', 'Annotate']

    # build a dictionary like {5101: {'Downloads':'x','Unzips':'',...}, }
    # then convert to an array of arrays and display
    grid = {}
    for header in headers[1:]:
        parseFilenames(config.folders[header.lower()], header, grid)

    # tabulate lib works like this -
    # print tabulate.tabulate([['Alice', 24], ['Bob', 19]], headers=['Name', 'Age'])
    # Name      Age
    # ------  -----
    # Alice      24
    # Bob        19

    rows = []
    volumes = filterVolumes or config.volumes
    for volume in volumes:
        # only include a row if it has some data
        gridrow = grid.get(volume)
        if gridrow:
            row = [gridrow.get(header) for header in headers]
            rows.append(row)
    print
    print tabulate.tabulate(rows, headers)
    print


if __name__ == '__main__':
    os.chdir('..')
    # vgList()
    vgList(['5101','5102','5103'])
    print 'done'



