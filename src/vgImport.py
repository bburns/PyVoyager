
"""
vg import command

Import Voyager .imq files to cube (.cub) files using ISIS voy2isis and
attach SPICE information with spiceinit.

The result is a set of ISIS level 0 cubes.

See https://isis.astrogeology.usgs.gov/Isis2/isis-bin/voyager_mosaic.cgi
    https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/voy2isis/voy2isis.html
    https://isis.astrogeology.usgs.gov/Application/presentation/Tabbed/spiceinit/spiceinit.html

Must run this from Linux

"""

import os.path

import config
import lib
import libimg
import libisis

import vgUnzip






def vgImport(pdsVol, optionOverwrite=False, directCall=True):

    """
    Import Voyager EDR files (.IMQ) to ISIS cube files (.CUB) for the given PDS volume,
    if folder doesn't exist yet.
    """

    pdsVol = str(pdsVol) # eg '5104'
    edrVols = lib.getEdrVols(pdsVol) # eg ['0013','0014']

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
            time = row[config.colFilesTime]

            #. for testing, just want 3 files
            # if fileId!='C1465335': continue
            # if fileId!='C1465337': continue
            # if fileId!='C1465339': continue

            # what edr volume does this image come from?
            edrVol = lib.getEdrVol(fileId)

            # get source IMQ file
            # eg step02_unzip/VG_0013/Jupiter/C1234XXX/C1234567.IMQ
            # sourceFile = lib.getFilepath('unzip', edrVol, target, fileId) # eh
            inputSubfolder = lib.getSubfolder('unzip', edrVol) # eg step02_unzip/VG_0013/
            subfolder = fileId[:5] + 'XXX/' # eg C1234XXX
            sourceFile = inputSubfolder + target + '/' + subfolder + fileId + '.IMQ'

            # missing source IMQ file?
            if not os.path.isfile(sourceFile):
                # missing file may be in RESTORED folder - check there.
                # this happened twice for voyager 1 at jupiter - not sure about other encounters.
                restoredFile = inputSubfolder + 'RESTORED/' + fileId + '.IRQ'
                if os.path.isfile(restoredFile):
                    lib.cp(restoredFile, sourceFile)
                else:
                    if target!='Dark':
                        print
                        print 'Warning: missing file - edr%s pds%s, %s' % (edrVol,pdsVol,sourceFile)
                        print
                    continue

            # get destination cubefile
            # eg step03_import/VGISS_5101/C1234567.cub
            destFile = lib.getFilepath('import', pdsVol, fileId)

            # if need to reimport a volume, can just use vg clear to remove it
            if os.path.isfile(destFile):
                print "File %d: %s already exists" % (nfile, destFile)

            else:

                # import IMQ file to CUB file
                # if image time is UNKNOWN, this will return nonzero, which throws an error -
                #   **ERROR** An unknown NAIF error has been encountered. The short explanation
                # provided by NAIF is [SPICE(INVALIDTIMESTRING)]. The Naif error is [The input
                # string contains an unrecognizable substring beginning at the character marked
                # by <U>: "<U>NKNOWN"].
                # filed issue here https://isis.astrogeology.usgs.gov/fixit/issues/4414
                # it does create a cubefile, but if use editlab on that, spiceinit fails
                # due to missing reseau info, so need to edit the IMQ file.
                s = "" # need to define this outside of the try block to pass it into except block
                try:
                    cmd = "voy2isis from=%s to=%s" % (sourceFile, destFile)
                    # cmd = "voy2isis from=%s to=%s 2>&1" % (sourceFile, destFile) #. nowork
                    print "File %d: %s" % (nfile, cmd)
                    s = lib.system(cmd)
                    #. how get the error string?
                except: # voy2isis will return nonzero, which throws an error
                    # print 's is',s #. nowork - s is always blank
                    # if "INVALIDTIMESTRING" in s:
                    try:
                        print "IMQ file missing image time - adding value %s from files.csv" % time

                        # make sure IMQ file has an IMAGE_TIME
                        libisis.updateImageTime(sourceFile, time)

                        # try command again
                        print
                        print "File %d: %s" % (nfile, cmd)
                        lib.system(cmd)
                        print

                    # elif "Unable to set PDS file" in s:
                    # else:
                    except:
                        print "voy2isis - error processing IMQ file - no cube file will be produced."
                        # print s
                        # continue
                    # else:
                        # print 'ss',s
                        # raise
                    # print



                # add spice info using ISIS spiceinit
                # print "Adding SPICE geometry info (using ISIS spiceinit)..."
                # this fails due to incomplete kernels - need to download and use some other kernels.
                # filed bugreport with isis - https://isis.astrogeology.usgs.gov/fixit/issues/4352
                # cmd = "spiceinit from=%s web=yes" % (destFile)
                tspk = "kernels/spk/jup100.bsp"
                spk = "kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
                cmd = "spiceinit from=%s TSPK=%s SPK=%s" % (destFile, tspk, spk)
                print "File %d: %s" % (nfile, cmd)
                try:
                    lib.system(cmd)
                except:
                    # also fails if missing target info, e.g. amalthea - assume that is the case here.
                    #.. but will catch error due to wrong kernels also, so will need to handle more kernels.
                    print "spiceinit - error attaching SPICE data - no camera pointing information available."
                    # continue


                # now we have level 0 files

            nfile += 1

            # #. stop after a few files, for testing
            # if nfile>10:
            #     print
            #     stop

    fFiles.close()

    print


if __name__ == '__main__':
    os.chdir('..')
    vgImport(5101)
    print 'done'

