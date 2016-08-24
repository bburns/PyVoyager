
"""
vg crop command

Crop/zoom in on images according to instructions in crops.csv.
"""

import os.path

import config
import lib
import libimg



def vgCrop(filterVolumes, optionOverwrite=False, directCall=True):
    
    "crop/zoom images in given volumes according to crops.csv"

    # filterVolume = str(filterVolume)
    # outputSubfolder = lib.getSubfolder('crop', filterVolume)

    # quit if volume folder exists
    # if os.path.isdir(outputSubfolder) and optionOverwrite==False:
    #     if directCall: print "Folder exists: " + outputSubfolder
    #     return

    # make sure folder is gone
    # lib.rmdir(outputSubfolder)
    
    volumeSeen = {}
    
    # read in crop info
    cropInfo = lib.readCsv(config.dbCrops)

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for row in csvFiles:
        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]

        if not volume in filterVolumes: continue # filter on desired volumes
        
        # make sure start with empty folder
        outputSubfolder = lib.getSubfolder('crop', volume)
        if not volume in volumeSeen:
            lib.rmdir(outputSubfolder)
            volumeSeen[volume] = True
        
        cropInfoRecord = cropInfo.get(fileId)
        if cropInfoRecord:

            # crops.csv has fileId, tx, ty, scale
            tx = int(cropInfoRecord['tx'])
            ty = int(cropInfoRecord['ty'])
            scale = float(cropInfoRecord['scale'])
            
            # get filenames
            infile = lib.getFilepath('composite', volume, fileId)
            outfile = lib.getFilepath('crop', volume, fileId)
            # print 'Volume %s cropping %d: %s       \r' % (volume,nfile,infile),
            print 'Volume %s cropping %d: %s       ' % (volume,nfile,infile)
            # print tx,ty,scale
            # print outfile

            # adjust the image
            if os.path.isfile(infile):
                # print 'pokpok'
                # make sure dest folder exists
                lib.mkdir(outputSubfolder)
                libimg.cropImageFile(infile, outfile, tx, ty, scale)
            else:
                print
                print 'Warning: missing image file', infile
            nfile += 1

    fFiles.close()
    # print

if __name__ == '__main__':
    os.chdir('..')
    vgCrop(5116, True)
    print 'done'

