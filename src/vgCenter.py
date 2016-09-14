
"""
vg center command

Currently this stabilizes images within a volume - ideally it would distribute
the images to their targets and then stabilize on that sequence, but this works
fairly well, with possible discontinuities at volume boundaries.

Build centers.csv file for a volume by centering and stablizing images in files.csv.
"""

import os
import os.path
import spiceypy as spice
import numpy as np
import math

import config
import lib
import libimg
import libspice
import log

import vgDenoise
import vgAdjust


# config.drawCrosshairs = True
# config.drawTarget = True

    

def getCubeHistory(cubefile):
    """
    get history of commands applied to given cubefile, as a list
    """
    
    # run ISIS cathist command
    cmd = "cathist from=%s" % cubefile
    s = lib.system(cmd)
    
    # parse the output
    history = []
    for line in s.split('\n'):
        if line.startswith('Object = '):
            obj = line[9:]
            history.append(obj)
            
    return history




def getExpectedTargetCenter(target, craft, camera, time):
    """
    get expected coordinates of target center px,py, in pixel space (0 to 800).
    returns px,py
    assumes libimg.loadKernels has been called.
    target is the target name, eg Jupiter.
    craft is Voyager1 or Voyager2.
    camera is Narrow or Wide.
    time is utc time as string.
    """
    
    # get target code
    targetId = spice.bodn2c(target) # eg 'Jupiter'->599

    # get spacecraft instrument        
    spacecraft = -31 if craft=='Voyager1' else -32
    spacecraftBus = spacecraft * 1000
    spacecraftScanPlatform = spacecraftBus - 100
    spacecraftNarrowCamera = spacecraftScanPlatform - 1
    spacecraftWideCamera = spacecraftScanPlatform - 2
    # instrument = spacecraftBus # use for NAIF continuous kernels
    instrument = spacecraftScanPlatform # use for PDS discrete kernels

    # get field of view and focal length
    # f is the focal length relative to the screen halfwidth of 1.0
    # i.e. screen coordinates are -1.0 to 1.0
    #. use ik
    print 'camera',camera
    fov = config.cameraFOVs[camera] # degrees - 0.424 or 3.169
    screenHalfwidth = 1.0
    f = screenHalfwidth / math.tan(fov/2 * math.pi/180) 
    print 'f=focal length',f
    
    # get ephemeris time
    # note: target and spacecraft locations are stored relative to J2000
    # time is utc time as string
    ephemerisTime = spice.str2et(time) # seconds since J2000 (will be negative)
    # sclkch = spice.sce2s(spacecraft, ephemerisTime) # spacecraft clock ticks, string
    # sclkdp = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock ticks, double
    clockTicks = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock ticks, double
    print 'clockTicks',clockTicks

    # get camera pointing matrix C
    # C is the world-to-camera transformation matrix.
    # ie C is a rotation matrix from the base frame 'frame' to
    # the instrument-fixed frame at the time clockTicks +/- tolerance.
    # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/ckgp_c.html
    tolerance = spice.sctiks(spacecraft, "0:00:800") # time tolerance
    frame = 'ECLIPB1950' # coordinate frame
    # ckgp is 'camera kernel get pointing'
    # note: the pointing information is stored in the time frame J2000,
    # but the coordinates are in the ECLIPB1950 coordinate frame.
    C, clkout, found = spice.ckgp(instrument, clockTicks, tolerance, frame)
    print 'C=camera pointing matrix - transform world to camera coords'
    print C

    # get position of target relative to spacecraft
    # this is the direction from craft to target in ECLIPB1950 frame
    observer = 'Voyager ' + craft[-1] # eg 'Voyager 1'
    frame = 'ECLIPB1950' # coordinate frame
    abberationCorrection = 'NONE'
    position, lightTime = spice.spkpos(target, ephemerisTime, frame,
                                       abberationCorrection, observer)
    print 'target position relative to observer', position

    # get position of target in camera space
    # position is in ECLIPB1950 units, but relative to camera space
    c = np.dot(C, position)
    print 'c=position in camera space',c

    # get screen coordinates of target (-1 to 1, -1 to 1)
    # S is the camera-to-screen transformation matrix.
    # sx=cx*f/cz; sy=cy*f/cz
    cz = c[2] # cz is the distance to the target along the z axis
    fz = f/cz
    # print 'fz=f/cz',fz
    S = np.array([[fz,0,0],[0,fz,0]]) 
    s = np.dot(S, c)
    print 's=screen space (-1 to 1)',s

    # get image coordinate (0 to 800, 0 to 800)
    # P would be a screen-to-pixel transformation matrix,
    # but would require converting to homogeneous coordinates in order
    # to include x,y translation.
    # p = -s * 800/2.0
    # p[0] = p[0]+400
    # p[1] = p[1]+400
    p = -s * 800/2.0 + 400 #.params
    print 'p=pixel space (0 to 800)',p
    px,py = p[0],p[1]
    
    # return px,py,fov
    return px,py


#. handle target
def vgCenter(filterVolume='', filterImageId='', optionOverwrite=False, directCall=True):
    
    "Build centered and stabilized images for given volume and write x,y,radius to centers.csv"

    filterVolume = str(filterVolume) # eg '5101'
    filterImageId = filterImageId.upper() # always capital C

    #. will eventually also want to fine tune stability in relation to previous and next image.

    
    if filterVolume!='':

        # eg step03_import/VGISS_5101/
        importSubfolder = lib.getSubfolder('import', filterVolume)
        
        jpegSubfolder = importSubfolder + 'jpegs/'
        # lib.rmdir(jpegSubfolder)
        lib.mkdir(jpegSubfolder)
        lib.rm(jpegSubfolder + '*.jpg')
        
    #     # #. just do adjust for now
    #     # # inputSubfolder = lib.getSubfolder('denoise', filterVolume)
    #     # inputSubfolder = lib.getSubfolder('adjust', filterVolume)
    #     # outputSubfolder = lib.getSubfolder('center', filterVolume)

    #     # # quit if volume folder exists
    #     # if os.path.isdir(outputSubfolder) and optionOverwrite==False:
    #     #     if directCall: print "Folder exists: " + outputSubfolder
    #     #     return

    #     # # build the previous images for the volume, if not already there
    #     # #. handle indiv images also - could lookup volume by fileid, call vgadjust here
    #     # vgAdjust.vgAdjust(filterVolume, '', optionOverwrite=False, directCall=False)
    #     # # vgDenoise.vgDenoise(filterVolume, optionOverwrite=False, directCall=False)
        
    #     # # create folder
    #     # lib.mkdir(outputSubfolder)

        # get number of files to process
        # nfiles = len(os.listdir(inputSubfolder))
        nfiles = len(os.listdir(importSubfolder))
    else:
        nfiles = 1

    # load spice kernels
    libspice.loadKernels()
        
    # read small dbs into memory
    centeringInfo = lib.readCsv(config.dbCentering) # when to turn centering on/off
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # open positions.csv file for target angular size info
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # open centers_new.csv file to write any new records to
    # csvNewCenters, fNewCenters = lib.openCsvWriter(config.dbCentersNew)

    # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
    lastImageInTargetSequence = {}

    # iterate through all available images, filter on desired volume or image
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for rowFiles in csvFiles:
        volume = rowFiles[config.colFilesVolume]
        fileId = rowFiles[config.colFilesFileId]
        
        # filter to given volume/image
        if volume!=filterVolume and fileId!=filterImageId: continue 

        # get image properties
        filter = rowFiles[config.colFilesFilter]
        system = rowFiles[config.colFilesSystem]
        craft = rowFiles[config.colFilesCraft]
        target = rowFiles[config.colFilesTarget]
        camera = rowFiles[config.colFilesCamera]
        time = rowFiles[config.colFilesTime]
        note = rowFiles[config.colFilesNote]

        # relabel target field if necessary
        target = lib.retarget(retargetingInfo, fileId, target)

        # get filename
        cubefile = lib.getFilepath('import', volume, fileId)

        # log.logr('Volume %s centering %d/%d: %s' % (volume,nfile,nfiles,infile))
        # log.logr('Volume %s centering %d/%d: %s' % (volume,nfile,nfiles,cubefile))
        # print 'Volume %s centering %d/%d: %s              \r' % (volume,nfile,nfiles,cubefile),
        nfile += 1

        if not os.path.isfile(cubefile):
            # print 'warning: missing file ' + cubefile
            pass #. for now
        else:
                        
            # get expected angular size (as fraction of frame) and radius
            imageFraction = lib.getImageFraction(csvPositions, fileId)
            targetRadius = int(400*imageFraction) #.param

            # do we actually need to center this image?
            doCenter = lib.centerThisImageQ(imageFraction, centeringInfo, fileId, note, target)
            if doCenter:

                # export to jpg so can analyze with opencv
                # (pngs take about same amt of time)
                print 'export to jpeg so can analyze with opencv'
                imagefile = jpegSubfolder + fileId + '.jpg'
                if not os.path.isfile(imagefile):
                    cmd = "isis2std from=%s to=%s format=jpeg" % (cubefile, imagefile)
                    print cmd
                    lib.system(cmd)

                # find center of target using blob and hough, then alignment to fixedimage
                # x,y is in pixels (0-800)
                # outfile = jpegSubfolder + fileId + '_centered.jpg'
                # x,y,foundRadius = libimg.centerImageFile(infile, outfile, targetRadius)
                # x,y,foundRadius = libimg.centerImageFile(imagefile, outfile, targetRadius)
                # x,y,foundRadius = libimg.centerImageFile(imagefile, None, targetRadius)
                # dx,dy,stabilizationOk = libimg.stabilizeImageFile(outfile, outfile, targetRadius)
                # if stabilizationOk:
                #     x += int(round(dx))
                #     y += int(round(dy))
                x,y = libimg.centerAndStabilizeImageFile(imagefile, targetRadius)
                print 'target actual',x,y
                
                # get expected target location in pixels (0-800)
                # px, py = getExpectedTargetCenter(target, craft, camera, time)
                px, py = getExpectedTargetCenter(target, craft, camera, time)
                print 'target expected',px,py
                
                #. draw target circle on image to verify centering fn
                # and expected location
                import cv2
                im = cv2.imread(imagefile)
                libimg.drawCircle(im,(int(x),int(y),targetRadius))
                libimg.drawCircle(im,(int(px),int(py),targetRadius), (0,0,255))
                cv2.imwrite(imagefile[:-4]+'circle.jpg', im)
                                  
                deltax = x - px
                deltay = y - py
                print 'deltax,y (px)',deltax, deltay
                
                #. use ik
                fov = config.cameraFOVs[camera] # degrees - 0.424 or 3.169
                
                angleDeltax = fov * deltax / 800 # degrees #. param
                angleDeltay = fov * deltay / 800
                print 'angledeltax,y (deg)',angleDeltax, angleDeltay
                
                # don't update the camera pointing angle twice!
                history = getCubeHistory(cubefile)
                print 'history',history
                if 'camrotate' in history:
                    angleDeltax = angleDeltay = 0
            
                #. build camrotate and put in a bin folder, add that to path
                camrotate = "/media/sf_bburns/Documents/@Projects/Voyager/src/camrotate/camrotate"
                cmd = "%s from=%s horizontal=%f vertical=%f twist=0" % \
                      (camrotate, cubefile, angleDeltax, angleDeltay)
                print cmd
                s = lib.system(cmd)
                print s
                
                #. parse s to get camera pointing matrix C
                # why? just for testing? 
                
                
                
                # stop
                

            #     # write x,y,radius to newcenters file
            #     rowNew = [fileId, volume, x, y, foundRadius]
            #     csvNewCenters.writerow(rowNew)

            # # don't really need to do this as further stages could just fall back on adjusted images
            # # else: # don't need to center image, so just copy as is
            #     #. should outfile keep the _denoised or _adjusted tag?
            #     # lib.cp(infile, outfile)
            

    fPositions.close()
    # fNewCenters.close()
    fFiles.close()

    # # now append newcenters records to centers file
    # if os.path.isfile(config.dbCentersNew):
    #     lib.concatFiles(config.dbCenters, config.dbCentersNew)
    #     lib.rm(config.dbCentersNew)
    #     print
    #     print 'New records appended to centers.csv file - please make sure any ' + \
    #           'older records are removed and the file is sorted before committing it to git'
    # else:
    #     print


if __name__ == '__main__':
    os.chdir('..')
    # vgCenter(5101)
    
    cubefile = 'data/step03_import/vgiss_5101/C1465335.cub'
    hist = getCubeHistory(cubefile)
    print hist
    
    print 'done'

