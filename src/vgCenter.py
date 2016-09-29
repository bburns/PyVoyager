
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

import cv2


import config
import lib
import libimg
import libspice
import log

import vgDenoise
import vgAdjust


# config.drawCrosshairs = True
# config.drawTarget = True

    

#. can just use brief mode
# Brief printout of a .cub history
# Description
# This example shows the cathist application in the brief mode.
# mirror from=peaks.cub to=temp.cub
# circle from=temp.cub to=temp2.cub
# Command Line
# cathist from=temp2.cub mode=brief
# Run the cahist application on a .cub file in brief mode.
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



def getCameraMatrix(craft, camera, time):
    """
    get the camera matrix for the given craft and camera at a utc time. 
    assumes libimg.loadKernels has been called.
    returns C, the 3x3 rotation matrix as a numpy array. 
    """
    
    # get target code
    # targetId = spice.bodn2c(target) # eg 'Jupiter'->599

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
    # print 'camera',camera
    fov = config.cameraFOVs[camera] # degrees - 0.424 or 3.169
    screenHalfwidth = 1.0
    f = screenHalfwidth / math.tan(fov/2 * math.pi/180) 
    # print 'f=focal length',f
    
    # get ephemeris time
    # note: target and spacecraft locations are stored relative to J2000
    # time is utc time as string
    ephemerisTime = spice.str2et(time) # seconds since J2000 (will be negative)
    # sclkch = spice.sce2s(spacecraft, ephemerisTime) # spacecraft clock ticks, string
    # sclkdp = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock ticks, double
    clockTicks = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock ticks, double
    # print 'clockTicks',clockTicks

    # # get position of target relative to spacecraft
    # # this is the direction from craft to target in ECLIPB1950 frame
    # observer = 'Voyager ' + craft[-1] # eg 'Voyager 1'
    # frame = 'ECLIPB1950' # coordinate frame
    # abberationCorrection = 'NONE'
    # position, lightTime = spice.spkpos(target, ephemerisTime, frame,
    #                                    abberationCorrection, observer)
    # print 'target position relative to observer', position

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
    # print 'C=camera pointing matrix - transform world to camera coords'
    # print C

    return C


def getTargetPosition(target, craft, camera, time):
    """
    get position of target in world coordinates relative to the observing craft.
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

    # get ephemeris time
    # note: target and spacecraft locations are stored relative to J2000
    # time is utc time as string
    ephemerisTime = spice.str2et(time) # seconds since J2000 (will be negative)
    # sclkch = spice.sce2s(spacecraft, ephemerisTime) # spacecraft clock ticks, string
    # sclkdp = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock ticks, double
    clockTicks = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock ticks, double
    # print 'clockTicks',clockTicks

    # get position of target relative to spacecraft
    # this is the direction from craft to target in ECLIPB1950 frame
    observer = 'Voyager ' + craft[-1] # eg 'Voyager 1'
    frame = 'ECLIPB1950' # coordinate frame
    abberationCorrection = 'NONE'
    position, lightTime = spice.spkpos(target, ephemerisTime, frame,
                                       abberationCorrection, observer)
    # print 'target position relative to observer', position

    return position
    


def getExpectedTargetCenter(target, craft, camera, time, C=None):
# def getExpectedTargetCenter(target, craft, camera, time):
    """
    Get expected coordinates of target center px,py, in pixel space (0 to 800).
    Returns px,py.
    Assumes libimg.loadKernels has been called to load all relevant SPICE kernels.
    target is the target name, eg Jupiter.
    craft is Voyager1 or Voyager2.
    camera is Narrow or Wide.
    time is utc time as string.
    Can also pass the camera pointing matrix C instead of using spice kernels. 
    """
    
    if C is None:
        C = getCameraMatrix(craft, camera, time)
        
    w = getTargetPosition(target, craft, camera, time)
    
    # get field of view and focal length
    # f is the focal length relative to the screen halfwidth of 1.0
    # i.e. screen coordinates are -1.0 to 1.0
    #. use ik
    # print 'camera',camera
    fov = config.cameraFOVs[camera] # degrees - 0.424 or 3.169
    screenHalfwidth = 1.0
    f = screenHalfwidth / math.tan(fov/2 * math.pi/180) 
    # print 'f=focal length',f
    
    # get position of target in camera space
    # position is in ECLIPB1950 units, but relative to camera space
    c = np.dot(C, w)
    # print 'c=position in camera space',c

    # get screen coordinates of target (-1 to 1, -1 to 1)
    # S is the camera-to-screen transformation matrix.
    # sx=cx*f/cz; sy=cy*f/cz
    cz = c[2] # cz is the distance to the target along the z axis
    fz = f/cz
    # print 'fz=f/cz',fz
    S = np.array([[fz,0,0],[0,fz,0]]) 
    s = np.dot(S, c)
    # print 's=screen space (-1 to 1)',s

    # get image coordinate (0 to 800, 0 to 800)
    # P would be a screen-to-pixel transformation matrix,
    # but would require converting to homogeneous coordinates in order
    # to include x,y translation.
    # p = -s * 800/2.0
    # p[0] = p[0]+400
    # p[1] = p[1]+400
    p = -s * 800/2.0 + 400 #.params
    p = 800 - p # rotate 180 degrees
    # print 'p=pixel space (0 to 800)',p
    px,py = p[0],p[1]
    
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
        nfiles = lib.getNfiles(importSubfolder)
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
                # if not os.path.isfile(imagefile):
                if 1:
                    cmd = "isis2std from=%s to=%s format=jpeg" % (cubefile, imagefile)
                    print cmd
                    lib.system(cmd)

                    
                # try solving for C given one worldpoint and pixelpoint
                # ---------------------------------------------------------------
                
                #. nowork yet with solvePnP - needs 3+ points
                
                #. this is possible with an interative soln - not sure how many points are required
                # but might need to program it to have more control over it,
                # eg use the existing roll amount
                # see http://mathworld.wolfram.com/EulerAngles.html
                
                # # world-to-camera transform (existing)
                # # get existing camera pointing matrix C,
                # # which is the world-to-camera transform.
                # # C is found in the existing c kernels,
                # # in which the pointing is off,
                # # but the roll about the z-axis is correct (hopefully always)
                # C = getCameraMatrix(craft, camera, time)
                # print 'Existing camera pointing matrix from Voyager .bsp kernels'
                # print C
                    
                # # try constructing a new C matrix, given a target in pixelspace and worldspace,
                # # and using the z-axis of the existing C.
                
                # # get target in pixelspace
                # # find center of target using blob and hough, then alignment to fixedimage
                # # px,py is in pixels (0-800)
                # px,py = libimg.centerAndStabilizeImageFile(imagefile, targetRadius)
                # p = np.array([px,py])
                # print 'target in pixelspace',p
                
                # # get target in worldspace
                # w = getTargetPosition(target, craft, camera, time)
                # print 'target in worldspace', w
                
                
                # # get field of view and focal length
                # # f is the focal length relative to the screen halfwidth of 1.0
                # # i.e. screen coordinates are -1.0 to 1.0
                # #. use ik
                # fov = config.cameraFOVs[camera] # degrees: 0.424 or 3.169
                # f = 1.0 / math.tan(fov/2 * math.pi/180) 

                # # get camera intrinsic matrix K
                # fx = f * 400.0
                # fy = f * 400.0
                # offsetx = 400.0
                # offsety = 400.0
                # K = np.array([[fx, 0, offsetx],
                #               [0, fy, offsety],
                #               [0,  0,       1]])
                # # print 'camera intrinsic matrix K'
                # # print K
                
                # #. use opencv solvePnP to get camera extrinsic matrix - rotation and translation
                # # *can pass initial guess and have it refine them
                # # ie we already have a rough C matrix, and translation is w?
                # # E = cv2.pnp(K)
                # # rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corners2, mtx, dist)
                # # retval, rvec, tvec = cv2.solvePnP(objectPoints, imagePoints, cameraMatrix, distCoeffs, useExtrinsicGuess, flags)
                # # objectPoints = np.array(w)
                # # imagePoints = np.array(p)
                # # objectPoints = np.array([w])
                # objectPoints = np.array([w],dtype=np.float)
                # imagePoints = np.array([p],dtype=np.float)
                # cameraMatrix = K
                # # cameraMatrix = np.array(K,dtype=np.float)
                # # distCoeffs = None
                # distCoeffs = np.zeros((5,1))
                # print objectPoints
                # print imagePoints
                # retval, rvec, tvec = cv2.solvePnP(objectPoints, imagePoints, cameraMatrix, distCoeffs)
                # print retval
                # print rvec
                # print tvec
                
                # print
                
                # stop

                # # so then you'd have a new C matrix
                # # convert to a quaternion
                # # and run some new isis program to update the camera pointing for the cube
                # # campoint or sthing
                # # camsetq
                # # camsetc
                

                
                # # get target in screenspace
                # # pixels-to-screen transform
                # s = (400 - p) / 400.0 #.params
                # sx = s[0]
                # sy = s[1]
                # print 'target in screenspace',s
                
                # # screen-to-camera transform
                
                # # get component of distance along camera z axis
                # distance = libspice.getDistance(w)
                # sdistance = math.sqrt(f**2 + sx**2 + sy**2) # complete the screen triangle, f=sz
                # czf = distance / sdistance
                
                # # target in cameraspace
                # cx = sx * czf
                # cy = sy * czf
                # cz = f * czf
                # c = [cx,cy,cz]
                
                # world-to-camera transform
                
                # we want to solve for world-to-camera transform Cnew
                # we have c=[cx,cy,cz] and w=[wx,wy,wz]
                # Cnew has 3 degrees of freedom, the 3 euler angles - yaw, pitch, roll
                # we get roll from the existing C matrix
                # so need to solve for yaw and pitch
                
                # does this need to be solved iteratively?
                # that's what isis seems to do

                # Cnew =
                # 

                
                # q = spice.m2q(C)
                # print 'q',q
                
                
                
                
                
                # try translating target to expected location
                # -------------------------------------------------------------------------
                
                # works, but will lose info as get closer to target
                
                # get actual target location in pixelspace
                # find center of target using blob and hough, then alignment to fixedimage
                # px,py is in pixels (0-800)
                px,py = libimg.centerAndStabilizeImageFile(imagefile, targetRadius)
                p = np.array([px,py])
                print 'target actual in pixelspace',p
                
                # get expected target location in pixelspace
                # based on existing C pointing kernels and spacecraft and target positions
                ex, ey = getExpectedTargetCenter(target, craft, camera, time)
                print 'target expected in pixelspace',ex,ey
                
                deltax = px - ex
                deltay = py - ey
                print 'deltax,y (pixels)',deltax,deltay
                
                # now translate the cubefile by deltax,deltay pixels
                cubefile2 = cubefile[:-4] + 'tr.cub'
                cmd = "translate from=%s to=%s ltrans=%f strans=%f" % \
                      (cubefile, cubefile2, -deltay, -deltax)
                print cmd
                s = lib.system(cmd)
                print s
                
                # print 'draw grid'
                # gridfile = cubefile[:-4] + '-grid.cub'
                # cmd = "grid from=%s to=%s" % (cubefile2, gridfile)
                # # cmd = "grid from=%s to=%s" % (cubefile, gridfile)
                # print cmd
                # lib.system(cmd)
                
                # print 'export to jpeg so can draw test circle'
                # # imagefile2 = imagefile[:-4] + 'tr.jpg'
                # imagefile2 = imagefile[:-4] + 'grid.jpg'
                # # cmd = "isis2std from=%s to=%s format=jpeg" % (cubefile2, imagefile2)
                # cmd = "isis2std from=%s to=%s format=jpeg" % (gridfile, imagefile2)
                # print cmd
                # lib.system(cmd)
                
                # print 'draw circles, export jpeg'
                # import cv2
                # im = cv2.imread(imagefile2)
                # libimg.drawCircle(im,(int(px),int(py),targetRadius), (0,255,0)) # green
                # libimg.drawCircle(im,(int(ex),int(ey),targetRadius), (0,0,255)) # red
                # # libimg.drawCircle(im,(int(ex2),int(ey2),targetRadius), (255,0,255))
                # cv2.imwrite(imagefile2[:-4]+'-circles.jpg', im)
                
                
                
                
                
                # get new C by rotating existing C by angle deltas 
                # -------------------------------------------------------------------------
                
                # angle deltas are based on target expected vs actual in pixelspace
                
                #. nowork yet - get sx,sy ~20-200
                
                # # get actual target location in pixelspace
                # # find center of target using blob and hough, then alignment to fixedimage
                # # px,py is in pixels (0-800)
                # px,py = libimg.centerAndStabilizeImageFile(imagefile, targetRadius)
                # p = np.array([px,py])
                # print 'target actual in pixelspace',p
                
                # # get expected target location in pixelspace
                # # based on existing C pointing kernels and spacecraft and target positions
                # ex, ey = getExpectedTargetCenter(target, craft, camera, time)
                # print 'target expected in pixelspace',[ex,ey]
                
                # deltax = ex - px
                # deltay = ey - py
                # print 'deltax,y (pixels)',[deltax,deltay]

                # # get field of view and focal length
                # # f is the focal length relative to the screen halfwidth
                # # screen coordinates are -1.0 to 1.0
                # #. use ik
                # fov = config.cameraFOVs[camera] # degrees - 0.424 or 3.169
                # # screenHalfwidth = 1.0
                # # f = screenHalfwidth / math.tan(fov/2 * math.pi/180) 
                
                # # get angle deltas
                # angleDeltax = fov * deltax / 800 # degrees #. param
                # angleDeltay = fov * deltay / 800
                
                # # angleDeltax = 0 #... just do vertical rotation for now (pitch)
                # # angleDeltay = 0 #... just do YAW
                
                # # note: this just depends on if you get rotation axes from rows or columns of C,
                # # because the inverse of C is just the transpose, since it's a rotation matrix.
                # # angleDeltax *= -1
                # # angleDeltay *= -1
                
                # angleTwist = 0
                # print 'angle deltas (deg)',[angleDeltax, angleDeltay, angleTwist]
                
                # # don't update the camera pointing angle twice!
                # #. actually these should come out to be ~zero if attempted twice, but check
                # history = getCubeHistory(cubefile)
                # # print 'history',history
                # if 'camrotate' in history:
                #     angleDeltax = angleDeltay = 0
                
                # #. install should build camrotate and put in a bin folder, add that to path
                # # the angles in order are aka pitch, yaw, rotate
                # cmd = "camrotate from=%s vertical=%.17f horizontal=%.17f twist=%.17f" % \
                #       (cubefile, angleDeltay, angleDeltax, angleTwist)
                # print cmd
                # # camrotate outputs the starting quaternion and end quaternion
                # s = lib.system(cmd)
                # print s
                
                # # get camera pointing matrix C, for testing
                # # get from new quaternion and convert to matrix with spice q2m
                # line = s.strip().split('\n')[-1]
                # values = line.split(',')[0:4]
                # q = [float(value) for value in values]
                # # print 'new q',q
                # C = spice.q2m(q)
                # # print 'new C'
                # # print C
                
                # # nowork - not sure why
                # # # get new expected target location in pixelspace
                # # ex2, ey2 = getExpectedTargetCenter(target, craft, camera, time, C)
                # # print 'new target expected location, pixelspace', [ex2,ey2]
                # # # deltax2, deltay2 = px-ex2, py-ey2
                # # deltax2, deltay2 = ex2-px, ey2-py
                # # print 'actual-new expected target location, px (want ~zero)', [deltax2, deltay2]
                # # angleDeltax2, angleDeltay2 = fov * deltax2/800, fov * deltay2/800
                # # print 'angle deltas (deg)', [angleDeltax2, angleDeltay2]
                
                
                # print 'draw grid'
                # gridfile = cubefile[:-4] + 'rot-grid.cub'
                # cmd = "grid from=%s to=%s" % (cubefile, gridfile)
                # print cmd
                # lib.system(cmd)
                
                # print 'export to jpeg'
                # imagefile2 = imagefile[:-4] + 'rot-grid.jpg'
                # cmd = "isis2std from=%s to=%s format=jpeg" % (gridfile, imagefile2)
                # print cmd
                # lib.system(cmd)
                    
                # # draw target circle on image to verify centering fn
                # # and expected location and updated location
                # print 'draw circles'
                # import cv2
                # im = cv2.imread(imagefile2)
                # libimg.drawCircle(im,(int(px),int(py),targetRadius), (0,255,0))
                # libimg.drawCircle(im,(int(ex),int(ey),targetRadius), (0,0,255))
                # # libimg.drawCircle(im,(int(ex2),int(ey2),targetRadius), (255,0,255))
                # cv2.imwrite(imagefile2[:-4]+'-circles.jpg', im)
                
                
                
                print
                
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

