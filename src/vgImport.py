
"""
vg import command

Import Voyager .imq files to cube (.cub) files using ISIS voy2isis.
"""

import os.path

import config
import lib
import libimg

import vgUnzip


def vgImport(pdsVol, optionOverwrite=False, directCall=True):

    "Import .imq files to .cub files for the given PDS volume, if .cub folder doesn't exist yet."

    pdsVol = str(pdsVol)
    edrVols = lib.getEdrVols(pdsVol) # eg ['13','14']
    # print edrVols
    
    outputSubfolder = lib.getSubfolder('import', pdsVol)
    # print outputSubfolder
    
    # quit if volume folder exists
    if os.path.isdir(outputSubfolder) and optionOverwrite==False:
        if directCall: print "Folder exists: " + outputSubfolder
        return

    # create dest folder
    lib.mkdir(outputSubfolder)

    for edrVol in edrVols:
        inputSubfolder = lib.getSubfolder('unzip', edrVol)
        # print inputSubfolder

        # unzip the download, if not already there
        vgUnzip.vgUnzip(edrVol, directCall=False)

        # run voy2isis on each imq file in subdirs
        print "Importing imqs to cubs for " + inputSubfolder
        exclude = set(['BROWSE', 'CALIB', 'DOCUMENT', 'INDEX', 'LABEL', 'RESTORED', 'SOFTWARE'])
        for root, dirs, files in os.walk(inputSubfolder, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            ndirs = len(dirs)
            if ndirs == 0: # ie we're at a leaf, with just files
                # print inputSubfolder, root, outputSubfolder
                for filename in files:
                    sourceFile = root + '/' + filename
                    destFile = outputSubfolder + filename[:-4] + '.cub'
                    cmd = "voy2isis from=%s to=%s" % (sourceFile, destFile)
                    print cmd + '               \r',
                    os.system(cmd)
        print


if __name__ == '__main__':
    os.chdir('..')
    vgImport(5101)
    print 'done'

