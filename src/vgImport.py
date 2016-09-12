
"""
vg import command

Import Voyager .imq files to cube (.cub) files using ISIS voy2isis and
attach SPICE information with spiceinit.
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
    
    importSubfolder = lib.getSubfolder('import', pdsVol)
    
    # quit if volume folder exists
    if os.path.isdir(importSubfolder) and optionOverwrite==False:
        if directCall: print "Folder exists: " + importSubfolder
        return

    # create dest folder
    lib.mkdir(importSubfolder)

    # unzip the downloads, if not already there
    for edrVol in edrVols:
        vgUnzip.vgUnzip(edrVol, directCall=False)

    # open files.csv for reading
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)

    # iterate over all available files
    nfile = 1
    for row in csvFiles:
        vol = row[config.colFilesVolume]
        if vol==pdsVol:
            fileId = row[config.colFilesFileId]
            target = row[config.colFilesTarget]
            
            edrVol = lib.getEdrVol(fileId)
            
            inputSubfolder = lib.getSubfolder('unzip', edrVol)
            subfolder = fileId[:5] + 'XXX/'
            sourceFile = inputSubfolder + target + '/' + subfolder + fileId + '.IMQ'
            # sourceFile = lib.getFilepath('unzip', edrVol, target
        
            if os.path.isfile(sourceFile):
                # destFile = importSubfolder + fileId + '.cub'
                destFile = lib.getFilepath('import', edrVol, fileId)
                cmd = "voy2isis from=%s to=%s" % (sourceFile, destFile)
                # print cmd
                print cmd + '               \r',
                lib.system(cmd)
                nfile += 1
                if nfile>10:
                    print
                    stop
                # stop
            else:
                #. missing file may be in RESTORED folder - check there
                if target!='Dark':
                    print
                    print 'Warning: missing file - edr%s pds%s, %s' % (edrVol,pdsVol,sourceFile)
                    print
    
    fFiles.close()
    
    print


if __name__ == '__main__':
    os.chdir('..')
    vgImport(5101)
    print 'done'

