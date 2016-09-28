
"""
vg list command

Show listing of volumes and what stage they're at.
"""

import os
import tabulate

import config
import lib


def parseFilenames(folder, section, grid):
    "parse dir+filenames in the given folder, add x to grid dictionary for volumes present"
    for root, dirnames, filenames in os.walk(folder):
        itemnames = dirnames
        itemnames.extend(filenames)
        for itemname in itemnames: # eg VGISS_5101.tar.gz, VG_0013.tar.gz
            if itemname.startswith('VGISS_'):
                volnum = itemname[6:10] # eg 5101
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Volume'] = volnum
                grid[volnum][section] = 'x'
            elif itemname.startswith('VG_'):
                volnum = itemname[3:7] # eg 0013
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Volume'] = volnum
                grid[volnum][section] = 'x'
        del dirnames[:] # don't recurse


def getGrid(headers):
    """
    build a dictionary like {5101: {'Downloads':'x','Unzips':'',...}, }
    """
    grid = {}
    for header in headers[1:]:
        step = header.lower()
        folder = lib.getFolder(step)
        parseFilenames(folder, header, grid)
    return grid


def getTable(grid, volumes, headers):
    """
    convert grid to a table (array of arrays)
    """
    table = []
    for volume in volumes:
        # only include a row if it has some data
        gridrow = grid.get(volume)
        if gridrow:
            row = [gridrow.get(header) for header in headers]
            table.append(row)
    return table


# def vgList(volnums=None, imageIds=None, targetPath=None):
def vgList(filterVolumes=''):

    "Get a listing of volumes and what stages they are at"

    # uses tabulate, which works like this -
    # print tabulate.tabulate([['Alice', 24], ['Bob', 19]], headers=['Name', 'Age'])
    # Name      Age
    # ------  -----
    # Alice      24
    # Bob        19

    edrAndPdsVolumes = list(config.edrVolumes)
    edrAndPdsVolumes.extend(config.volumes)
    volumes = filterVolumes or edrAndPdsVolumes

    # headers = ['Volume', 'Download', 'Unzip', 'Convert', 'Adjust',
               # 'Denoise', 'Center', 'Inpaint', 'Composite', 'Mosaic', 'Annotate']

    # headers = ['Volume', 'Download', 'Unzip']

    headers = ['Volume', 'Download', 'Unzip', 'Import']

    grid = getGrid(headers)
    table = getTable(grid, volumes, headers)
    s = tabulate.tabulate(table, headers)

    print
    print s
    print

    # pdsHeaders = ['PDS Vol', 'Import', 'Convert', 'Adjust', 'Denoise', 'Center',
                  # 'Inpaint', 'Composite', 'Mosaic', 'Annotate']


if __name__ == '__main__':
    os.chdir('..')
    vgList()
    # vgList(['0013','0014','0015'])
    # vgList(['5101','5102','5103'])
    print 'done'



