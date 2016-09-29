
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

import vgUnzip




def getNextRecord(f):
    "Get next variable-length record and the position of its contents in the file"
    low = ord(f.read(1))
    high = ord(f.read(1))
    nbytes = high * 256 + low
    startPos = f.tell()
    s = f.read(nbytes)
    if (nbytes % 2) == 1:
        f.read(1) # read padding byte
    return s, startPos

def getImageTimeRecord(f):
    "Search through records for IMAGE_TIME and return entire record and start file position"
    imageTimeRecord = None
    startPos = None
    while True:
        s, startPos = getNextRecord(f)
        if s.startswith('IMAGE_TIME'):
            imageTimeRecord = s
            break
        if s == 'END':
            break
    return imageTimeRecord, startPos

def updateImageTime(sourceFile, time):
    "Replace IMAGE_TIME=UNKNOWN label in the given file with a UTC time"
    # the IMQ file record fortunately has lots of spaces in it so can
    # fit the new time into it
    f = open(sourceFile, 'rb+')
    imageTimeRecord, startPos = getImageTimeRecord(f)
    if imageTimeRecord.endswith('UNKNOWN'):
        # print "IMAGE_TIME is UNKNOWN - replacing with time value from dbFiles.csv"
        # print sourceFile
        # print imageTimeRecord
        # print time
        # print startPos
        newImageTimeRecord = 'IMAGE_TIME = ' + time + 'Z'
        nspaces = len(imageTimeRecord) - len(newImageTimeRecord)
        newImageTimeRecord += ' ' * nspaces
        # print newImageTimeRecord
        f.seek(startPos)
        f.write(newImageTimeRecord)
        # print
    f.close()



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
                # but it does create the cubefile, so can edit the label with the actual time
                # from files.csv.
                try:
                    cmd = "voy2isis from=%s to=%s" % (sourceFile, destFile)
                    print "File %d: %s" % (nfile, cmd)
                    lib.system(cmd)
                except: # voy2isis will return nonzero, which throws an error
                    print
                    print "IMQ missing image time - adding value %s from files.csv" % time

                    # make sure IMQ file has an IMAGE_TIME
                    updateImageTime(sourceFile, time)

                    # try command again
                    print
                    print "File %d: %s" % (nfile, cmd)
                    lib.system(cmd)

                # add spice info using ISIS spiceinit
                # print "Adding SPICE geometry info (using ISIS spiceinit)..."
                # this fails due to incomplete kernels - need to download and use some other kernels.
                # filed bugreport with isis - https://isis.astrogeology.usgs.gov/fixit/issues/4352
                # cmd = "spiceinit from=%s web=yes" % (destFile)
                tspk = "kernels/spk/jup100.bsp"
                spk = "kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp"
                cmd = "spiceinit from=%s TSPK=%s SPK=%s" % (destFile, tspk, spk)
                print "File %d: %s" % (nfile, cmd)
                lib.system(cmd)


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

