
import os
import tabulate

import config



def buildList():
    "get a listing of volumes and what stages they are at"

    # build a dictionary like {5101: {'Downloads':True,'Unzips':False,...}, }
    # then convert to an array of arrays and display
    grid = {}
    for root, dirnames, filenames in os.walk(config.downloadsFolder):
        for filename in filenames: # eg VGISS_5101.tar.gz
            if filename[-6:]=='tar.gz':
                volnum = filename[6:10] # eg 5101
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Downloads'] = 'x'
        del dirnames[:] # don't recurse

    for root, dirnames, filenames in os.walk(config.unzipsFolder):
        for dirname in dirnames: # eg VGISS_5101
            if dirname[:6]=='VGISS_':
                volnum = dirname[6:10] # eg 5101
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Unzips'] = 'x'
        del dirnames[:] # don't recurse

    for root, dirnames, filenames in os.walk(config.imagesFolder):
        for dirname in dirnames: # eg VGISS_5101
            if dirname[:6]=='VGISS_':
                volnum = dirname[6:10] # eg 5101
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Images'] = 'x'
        del dirnames[:] # don't recurse

    for root, dirnames, filenames in os.walk(config.centersFolder):
        for dirname in dirnames: # eg VGISS_5101
            if dirname[:6]=='VGISS_':
                volnum = dirname[6:10] # eg 5101
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Centers'] = 'x'
        del dirnames[:] # don't recurse

    for root, dirnames, filenames in os.walk(config.compositesFolder):
        for dirname in dirnames: # eg VGISS_5101
            if dirname[:6]=='VGISS_':
                volnum = dirname[6:10] # eg 5101
                if not grid.get(volnum): grid[volnum] = {}
                grid[volnum]['Composites'] = 'x'
        del dirnames[:] # don't recurse

    # print tabulate.tabulate([['Alice', 24], ['Bob', 19]], headers=['Name', 'Age'])
    headers = ['Volume', 'Downloads', 'Unzips', 'Images', 'Centers', 'Composites']
    rows = []
    for vol in config.volumes:
        # only include a row if it has some data
        svol = str(vol)
        gridrow = grid.get(svol)
        if gridrow:
            row = [svol, gridrow.get('Downloads'), gridrow.get('Unzips'), gridrow.get('Images'), gridrow.get('Centers'), gridrow.get('Composites')]
            rows.append(row)

    print
    print tabulate.tabulate(rows, headers)
    print


if __name__ == '__main__':
    os.chdir('..')
    buildList()
    print 'done'



