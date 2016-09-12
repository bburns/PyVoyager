
"""
vg import command

Import Voyager .imq files to cube (.cub) files using ISIS voy2isis and
attach SPICE information with spiceinit.
The result is a set of ISIS level 0 cubes.
"""

import os.path

import config
import lib
import libimg

import vgUnzip


def vgImport(pdsVol, optionOverwrite=False, directCall=True):

    "Import .imq files to .cub files for the given PDS volume, if .cub folder doesn't exist yet."

    pdsVol = str(pdsVol) # eg '5104'
    edrVols = lib.getEdrVols(pdsVol) # eg ['13','14']
    
    importSubfolder = lib.getSubfolder('import', pdsVol) # eg 'step03_import/VGISS_5104'
    
    # quit if volume folder exists
    if os.path.isdir(importSubfolder) and optionOverwrite==False:
        if directCall: print "Folder exists: " + importSubfolder
        return

    # create import folder
    lib.mkdir(importSubfolder)

    # unzip the EDR archives to IMQ files, if not already done
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
            
            # what edr volume does this image come from? 
            edrVol = lib.getEdrVol(fileId)
            
            # get sourcefile, eg step02_unzip/VG_13/Jupiter/C1234XXX/C1234567.IMQ
            inputSubfolder = lib.getSubfolder('unzip', edrVol)
            subfolder = fileId[:5] + 'XXX/'
            sourceFile = inputSubfolder + target + '/' + subfolder + fileId + '.IMQ'
            # sourceFile = lib.getFilepath('unzip', edrVol, target
        
            if os.path.isfile(sourceFile):
                # get destfile, eg step03_import/VGISS_5101/C1234567.cub
                # destFile = importSubfolder + fileId + '.cub'
                destFile = lib.getFilepath('import', pdsVol, fileId)
                cmd = "voy2isis from=%s to=%s" % (sourceFile, destFile)
                print cmd
                # print cmd + '               \r',
                lib.system(cmd)
                
                # fails due to incomplete kernels
                # cmd = "spiceinit from=%s" % (destFile)
                # print cmd
                # lib.system(cmd)
                
                # add spice info (spiceinit)
                # print "Adding SPICE geometry info (spiceinit)..."
                # voydir = os.getcwd()
                # os.chdir(importSubfolder)
                # cmd = "parallel spiceinit from={} web=yes ::: *.cub" # error on some imq's
                # parallel spiceinit from={} \
                #     TSPK=/home/bburns/Desktop/Voyager/kernels/spk/jup100.bsp \
                #     SPK=/home/bburns/Desktop/Voyager/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp \
                #     ::: *.cub
                # parallel spiceinit from={} \
                    # TSPK=$VOYAGER/kernels/spk/jup100.bsp \
                    # SPK=$VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp \
                    # ::: *.cub
                # tspk = "../../../kernels/spk/jup100.bsp"
                # spk = "../../../kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
                # tspk = "$VOYAGER/kernels/spk/jup100.bsp"
                # spk = "$VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
                # tspk = voydir + "/kernels/spk/jup100.bsp"
                # spk = voydir + "/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
                # cmd = "parallel spiceinit from={} TSPK=%s SPK=%s ::: C???????.cub" % (tspk, spk)
                tspk = "kernels/spk/jup100.bsp"
                spk = "kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
                cmd = "spiceinit from=%s TSPK=%s SPK=%s" % (destFile, tspk, spk)
                print cmd
                lib.system(cmd)
                # print

                # now we have level 0 files
                
                nfile += 1
                #. stop after a few files, for testing
                if nfile>10:
                    print
                    stop
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

