
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
    # edrVols,fileRange = lib.getEdrVols(pdsVol) # eg ['13','14']
    # print edrVols
    
    outputSubfolder = lib.getSubfolder('import', pdsVol)
    # print outputSubfolder
    
    # quit if volume folder exists
    if os.path.isdir(outputSubfolder) and optionOverwrite==False:
        if directCall: print "Folder exists: " + outputSubfolder
        return

    # create dest folder
    lib.mkdir(outputSubfolder)

    # unzip the downloads, if not already there
    for edrVol in edrVols:
        vgUnzip.vgUnzip(edrVol, directCall=False)

    # open files.csv for reading
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)

    # iterate over all available files
    for row in csvFiles:
        vol = row[config.colFilesVolume]
        if vol==pdsVol:
            fileId = row[config.colFilesFileId]
            target = row[config.colFilesTarget]
            
            edrVol = lib.getEdrVol(fileId)
            
            inputSubfolder = lib.getSubfolder('unzip', edrVol)
            subfolder = fileId[:5] + 'XXX/'
            sourceFile = inputSubfolder + target + '/' + subfolder + fileId + '.IMQ'
        
            if os.path.isfile(sourceFile):
                destFile = outputSubfolder + fileId + '.cub'
                cmd = "voy2isis from=%s to=%s" % (sourceFile, destFile)
                # print cmd
                print cmd + '               \r',
                os.system(cmd)
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

