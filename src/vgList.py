
"""
vg list command

Show listing of volumes and what stage they're at.
"""

import os
import tabulate

import config


def parseFilenames(folder, section, grid):
    "parse filenames in the given folder, add x to grid dictionary for volumes present"
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


# def vgList(pVolume=None, pImageId=None, pTargetPath=None):
# def vgList(volnums=None, imageIds=None, targetPath=None):
def vgList(volnums):
    "Get a listing of volumes and what stages they are at"

    # build a dictionary like {5101: {'Downloads':'x','Unzips':'',...}, }
    # then convert to an array of arrays and display
    grid = {}
    parseFilenames(config.downloadsFolder, 'Downloads', grid)
    parseFilenames(config.unzipsFolder, 'Unzips', grid)
    parseFilenames(config.imagesFolder, 'Images', grid)
    parseFilenames(config.adjustmentsFolder, 'Adjustments', grid)
    parseFilenames(config.denoisedFolder, 'Denoised', grid)
    parseFilenames(config.centersFolder, 'Centers', grid)
    parseFilenames(config.compositesFolder, 'Composites', grid)

    # tabulate lib works like this -
    # print tabulate.tabulate([['Alice', 24], ['Bob', 19]], headers=['Name', 'Age'])
    # Name      Age
    # ------  -----
    # Alice      24
    # Bob        19

    headers = ['Volume', 'Downloads', 'Unzips', 'Images', 'Adjustments',
               'Denoised', 'Centers', 'Composites']
    rows = []
    # for vol in config.volumes:
    volumes = volnums or config.volumes
    for vol in volumes:
        # only include a row if it has some data
        svol = str(vol)
        gridrow = grid.get(svol)
        if gridrow:
            row = [gridrow.get(header) for header in headers]
            rows.append(row)
    print
    print tabulate.tabulate(rows, headers)
    print


if __name__ == '__main__':
    os.chdir('..')
    vgList()
    print 'done'



