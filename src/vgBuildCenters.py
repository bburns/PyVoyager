
# build centered images from plain png images

import csv
import os
import os.path

import config
import lib
import libimg
import db
    
import vgBuildImages


def buildCenters(volnum, overwrite=False):
    "build centered images for given volume, if they don't exist yet"
    
    imagesubfolder = config.imagesFolder + 'VGISS_' + str(volnum) + '/'
    centersubfolder = config.centersFolder + 'VGISS_' + str(volnum) + '/'
    
    if int(volnum)==0: # test volume - turn on image debugging
        config.drawBoundingBox = True
        config.drawCircle = True
        config.drawCrosshairs = True
        
    if int(volnum)!=0 and os.path.isdir(centersubfolder) and overwrite==False: # for test (vol=0), can overwrite test folder
        print "Folder exists - skipping vg images step: " + centersubfolder
    else:
        vgBuildImages.buildImages(volnum) # build the plain images for the volume, if not already there

        # make new folder
        lib.rmdir(centersubfolder)
        lib.mkdir(centersubfolder)

        centeringInfo = lib.readCsv('db/centering.csv') # get dictionary of dictionaries
        
        # iterate through all available images, filter on desired volume
        f = open(config.filesdb, 'rt')
        i = 0
        reader = csv.reader(f)
        volnum = str(volnum) # eg '5101'
        nfile = 1
        for row in reader:
            if row==[] or row[0][0]=="#":
                pass
            if i==0:
                fields = row
            else:
                volume = row[config.filesColVolume]
                if volume==volnum:
                    fileId = row[config.filesColFileId]
                    filter = row[config.filesColFilter]
                    system = row[config.filesColPhase]
                    craft = row[config.filesColCraft]
                    target = row[config.filesColTarget]
                    camera = row[config.filesColInstrument]
                    
                    # get the centering info, if any
                    # info includes planetCraftTargetCamera,centeringOff,centeringOn
                    planetCraftTargetCamera = system + craft + target + camera
                    info = centeringInfo.get(planetCraftTargetCamera)
                    if info:
                        centeringOff = info['centeringOff']
                        centeringOn = info['centeringOn']
                        docenter = fileId<centeringOff or fileId>centeringOn
                    else: # if no info for this target just center it
                        docenter = True

                    # center the file
                    pngfilename = fileId + '_' + config.imageType + '_' + filter + '.png'
                    infile = imagesubfolder + pngfilename
                    outfile = centersubfolder + config.centersPrefix + pngfilename
                    # print 'centering %d/%d: %s' %(nfile,nfiles,infile)
                    # print 'centering %d: %s' %(nfile,infile)
                    print '\rcentering %d: %s' %(nfile,infile),
                    libimg.adjustImageFile(infile, outfile, docenter)
                        
                    nfile += 1

            i += 1

        f.close()
    

if __name__ == '__main__':
    os.chdir('..')
    buildCenters(0)
    print 'done'


    
