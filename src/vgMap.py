
"""
vg map command

Build up 2d color maps of targets
"""

# this had been starting to work as part of the original pipeline,
# taking a centered image and projecting it to a map.
# then i discovered isis.
# isis is slow though so rearranged it to work with isis cubefiles
# to compare the speed.
# this is about 2x as fast as isis, but not worth reimplementing all
# that functionality.

# so, will mothball this


import os
import os.path
import sys

import numpy as np
# import linalg from numpy
import cv2
import math
# import spiceypy as spice


# import sys; p = ['SpiceyPy']; p.extend(sys.path); sys.path = p
# print sys.path
import spiceypy as spice
# print spice.bodeul
# print help(spice.bodeul)
# spice.foo()
# stop



import config
import lib
import libimg
import libspice
import log



def getCameraMatrix(frame, spacecraft, instrument, ephemerisTime):
    """
    Get camera pointing matrix C.
    This is the world-to-camera matrix, from the base frame to the
    given instrument's fixed frame at the given ephemeris time.
    """
    sclkdp = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock double
    # sclkch = spice.sce2s(spacecraft, ephemerisTime) # spacecraft clock string
    # print 'sclkdp',sclkdp
    # see https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/ckgp_c.html
    tolerance = spice.sctiks(spacecraft, "0:00:800") # time tolerance
    C, clkout, found = spice.ckgp(instrument, sclkdp, tolerance, frame)
    if not found:
        print 'camera pointing matrix not found for time', sclkdp
        # continue
        C = None
    return C


def getNorthPoleAngle(target, position, C, B, camera):
    """
    Get angle north pole of target makes with image y-axis, in radians.
    """

    # get target spin axis
    # the last row of the matrix is the north pole vector, *per spice docs*
    # seems correct, as it's nearly 0,0,1
    Bz = B[2]
    print 'Bz=north pole spin axis',Bz

    # get target radius, km
    nvalues, radii = spice.bodvrd(target, 'RADII', 3)
    targetRadiusEquator = (radii[0] + radii[1]) / 2
    targetRadiusPoles = radii[2]
    targetRadius = sum(radii) / 3
    # flatteningCoefficient = (targetRadiusEquator - targetRadiusPoles) / targetRadiusEquator
    # print 'target radius in km', targetRadius

    # get north pole location
    positionNP = position + targetRadius * Bz
    print 'positionNP=north pole in world coords', positionNP

    # get target position in camera space
    c = np.dot(C, position)
    cNP = np.dot(C, positionNP)
    print 'c=position in camera space',c
    print 'cNP=north pole in camera space',cNP

    # get camera fov and focal length
    fovDegrees = config.cameraFOVs[camera] # 0.424 or 3.169 deg
    fovRadians = fovDegrees * math.pi / 180
    f = 1.0 / math.tan(fovRadians/2) # focal length (relative to screen halfwidth of 1.0)
    print 'f=focal length',f

    # get camera-to-screen matrix S
    cz = c[2]
    fz = f/cz
    # print 'fz=f/cz',fz
    S = np.array([[fz,0,0],[0,fz,0]])

    # get screen coordinate (-1 to 1, -1 to 1)
    s = np.dot(S, c)
    sNP = np.dot(S, cNP)
    # ie sx=cx*f/cz; sy=cy*f/cz
    print 's=screen space (-1 to 1)',s
    print 'sNP=screen space north pole (-1 to 1)',sNP

    # get angle between north pole and image y-axis
    npDelta = sNP-s
    npRadians = math.atan(npDelta[0]/npDelta[1])
    npAngle = npRadians * 180/math.pi
    print 'npAngle',npAngle

    return npRadians


def drawNorthPole(im, s, sNP):
    "draw north pole on image"

    # get image coordinate (0 to 800, 0 to 800)
    p = -s * 800/2.0
    p[0] = p[0]+400
    p[1] = p[1]+400
    pNP = -sNP * 800/2.0
    pNP[0] = pNP[0]+400
    pNP[1] = pNP[1]+400
    print 'p=pixel space (0 to 800)',p
    print 'pNP=pixel space north pole (0 to 800)',pNP

    pt1 = tuple([int(x) for x in p])
    pt2 = tuple([int(x) for x in pNP])
    im = cv2.line(im, pt1, pt2, 128) # last number is grayscale level

    return im




def vgMap(filterVolumes=None, optionOverwrite=False, directCall=True):

    "Build up 2d color map"

    # # cmd = "echo $ISISROOT"
    # cmd = "env | ag ^ISIS"
    # s = lib.system(cmd)
    # print s


    # load SPICE kernels (data files) with camera and target positions, etc
    libspice.loadKernels()

    # read small dbs into memory
    # centeringInfo = lib.readCsv(config.dbCentering) # when to turn centering on/off
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions) # for target size

    # # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
    # lastImageInTargetSequence = {}

    # size of 2d map
    mymax = 800
    mxmax = 2 * mymax
    mxcenter = mxmax/2
    mycenter = mymax/2

    # set up blank mapping arrays: h(x,y) = (hx(x,y), hy(x,y))
    # h tells map where to pull its pixels from - ie map(mx,my) = im(h(mx,my))
    hx = np.zeros((mymax,mxmax),np.float32)
    hy = np.zeros((mymax,mxmax),np.float32)

    # make blank maps for each color channel
    #. each system-craft-target-camera-channel will need its own png map file to write to and colorize from
    # store in a map folder
    # bluemap = np.zeros((mymax,mxmax),np.float32)
    bluemap = np.zeros((mymax,mxmax),np.uint8)
    # each might also need a count map, if wind up averaging things together to smooth things out
    # would prefer to avoid it if possible though - adds more complexity and i/o
    countmap = np.zeros((mymax,mxmax),np.uint8)

    # iterate through all available images, filter on desired volume or image
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    nfile = 1
    for rowFiles in csvFiles:
        volume = rowFiles[config.colFilesVolume]
        fileId = rowFiles[config.colFilesFileId]

        # filter to given volume
        # if volume!=filterVolume: continue

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

        #. skip others
        if fileId!='C1465335': continue

        # get cube filename
        cubefile = lib.getFilepath('import', volume, fileId)
        if not os.path.isfile(cubefile):
            # print 'warning file not found', cubefile
            continue #. for now


        # get folders
        importSubfolder = lib.getSubfolder('import', volume)
        jpegSubfolder = importSubfolder + 'jpegs/'
        # mapSubfolder = importSubfolder + 'maps/'
        mapSubfolder = importSubfolder #. for now
        lib.mkdir(jpegSubfolder)
        lib.mkdir(mapSubfolder)

        # export as jpeg
        imagefile = jpegSubfolder + fileId + '.jpg'
        # if not os.path.isfile(imagefile):
        if 1:
            cmd = "isis2std from=%s to=%s format=jpeg" % (cubefile, imagefile)
            print cmd
            lib.system(cmd)

        # print 'Volume %s mapping %d: %s      \r' % (volume,nfile,infile),
        # print 'Volume %s mapping %d: %s' % (volume,nfile,infile)
        nfile += 1


        # get target code, eg Jupiter
        targetId = spice.bodn2c(target) # eg 'Jupiter'->599
        # print target, targetId

        # get instrument
        spacecraft = -31 if craft=='Voyager1' else -32
        spacecraftBus = spacecraft * 1000 # eg -31000
        spacecraftScanPlatform = spacecraftBus - 100 # eg -31100
        spacecraftNarrowCamera = spacecraftScanPlatform - 1 # eg -31101
        spacecraftWideCamera = spacecraftScanPlatform - 2 # eg -31102
        # instrument = spacecraftBus # eg -31000, use for NAIF continuous kernels
        instrument = spacecraftScanPlatform # eg -31100, use for PDS discrete kernels

        # get ephemeris time
        ephemerisTime = spice.str2et(time) # seconds since J2000 (will be negative)

        # world coordinate frame to use
        # (ECLIPB1950 is how the voyager and planet positions are encoded)
        frame = 'ECLIPB1950'

        # get world-to-camera matrix (camera pointing matrix)
        # C is a transformation matrix from ELIPB1950 to the instrument-fixed frame
        # at the given time
        C = getCameraMatrix(frame, spacecraft, instrument, ephemerisTime)
        print 'C=camera pointing matrix - transform world to camera coords'
        print C

        # get world-to-body matrix
        # B = getBodyMatrix(frame, targetId, ephemerisTime)
        B = spice.tipbod(frame, targetId, ephemerisTime)
        print 'B=world to body/target frame matrix'
        print B


        # get boresight vector
        # this is just the third row of the C-matrix, *per spice docs*
        boresight = C[2]
        print 'boresight pointing vector',boresight

        # get location of prime meridian
        rotationRate = 870.5366420 # deg/day for great red spot
        primeMeridian = rotationRate /24/60/60 * ephemerisTime # deg
        print 'primeMeridian (deg)', primeMeridian % 360
        primeMeridianRadians = primeMeridian * math.pi/180

        # get target position in world coordinates
        # ie vector from craft to target
        # and distance
        observer = 'Voyager ' + craft[-1] # eg Voyager 1
        abberationCorrection = 'NONE'
        position, lightTime = spice.spkpos(target, ephemerisTime, frame,
                                           abberationCorrection, observer)
        # position = getObserverToTargetVector(frame, observer, target, ephemerisTime)
        distance = libspice.getDistance(position)
        posnormal = position / distance
        print 'target position relative to observer',position
        print 'distance in km',distance
        print 'position normalized', posnormal

        # see how different boresight and position vector are
        dot = np.dot(boresight, posnormal)
        theta = math.acos(dot) * 180/math.pi
        print 'angle between boresight and position vector', theta


        # what longitudes are visible?
        #.. get from position of craft
        visibleLongitudesMin = 0
        visibleLongitudesMax = math.pi

        # get tilt of north pole relative to image y-axis
        npRadians = getNorthPoleAngle(target, position, C, B, camera)

        # get axial tilt rotation matrix
        cc = math.cos(npRadians)
        ss = math.sin(npRadians)
        mTilt = np.array([[cc,-ss],[ss,cc]])

        # get expected angular size (as fraction of frame) and radius
        imageFraction = lib.getImageFraction(csvPositions, fileId)
        targetRadiusPx = int(400*imageFraction) #.param

        # read the (centered) image
        im = cv2.imread(imagefile)

        # draw the target's north pole on image
        # im = drawNorthPole(im)

        # build hx,hy arrays, which tell map where to pull pixels from in source image
        # m: map (0 to mxmax, 0 to mymax)
        r = targetRadiusPx # pixels
        for mx in xrange(mxmax): # eg 0 to 1600
            for my in xrange(mymax): # eg 0 to 800

                # q: map (0 to 2pi, -1 to 1)
                qx = float(mx) / mxmax * 2 * math.pi + primeMeridianRadians
                qx = qx % (2 * math.pi) # 0 to 2pi
                qy = -float(my-mycenter)/mycenter # 1 to -1

                # s: image (-1 to 1, -1 to 1)
                sx = -math.sqrt(1 - qy**2) * math.cos(qx) # -1 to 1
                sy = qy # 1 to -1

                # rotate s to account for axial tilt relative to camera up axis
                # ie s = mTilt * s
                s = np.array([sx,sy])
                s = np.dot(mTilt,s)
                sx,sy = s

                # p: image (0 to 800, 0 to 800)
                px = sx * r + 400 # 0 to 800
                py = -sy * r + 400 # 0 to 800

                # hx[my][mx] = px
                # hy[my][mx] = py
                visible = (qx >= visibleLongitudesMin) and (qx <= visibleLongitudesMax)
                if visible:
                    hx[my][mx] = px
                    hy[my][mx] = py
                else:
                    hx[my][mx] = 0
                    hy[my][mx] = 0

        # do map projection
        map = cv2.remap(im, hx, hy, cv2.INTER_LINEAR)
        map = map[:,:,0]
        # map = np.array(map, np.float32)
        libimg.show(map)

        # save map as png file
        mapfile = mapSubfolder + fileId + '-map.png'
        cv2.imwrite(mapfile, map)

        sys.exit(0)


        # #. now need to blend this into the main map for this filter

        # # print type(map[0][0])
        # # print type(bluemap[0][0])

        # # bluemap = cv2.addWeighted(bluemap, 0.5, map, 0.5, 0)

        # # ret, countzero = cv2.threshold(countmap, 0,255, cv2.THRESH_BINARY)
        # # ret, countone = cv2.threshold(countmap, 0,255, cv2.THRESH_BINARY)
        # # countzero = 255-countone
        # # ret, mapMask = cv2.threshold(map, 1, 255, cv2.THRESH_BINARY)
        # # mapMask = cv2.bitwise_and(countzero, mapMask)
        # # c = mapMask & 1
        # # countmap += c

        # # libimg.show(countmap)

        # # ret, mapnonzero = cv2.threshold(map, 0,1, cv2.THRESH_BINARY)
        # ret, mapnonzero = cv2.threshold(map, 1,1, cv2.THRESH_BINARY)

        # countmapPlusOne = countmap + 1
        # countmap2 = countmap + 1-mapnonzero
        # base = np.array(bluemap, np.float32)
        # # base = base * countmap / countmapPlusOne
        # base = base * countmap2 / countmapPlusOne
        # newmap = np.array(map, np.float32)
        # newmap = newmap / countmapPlusOne
        # newbase = base + newmap
        # newbase = np.array(newbase, np.uint8)

        # # increment countmap where map image data exists
        # countmap += mapnonzero
        # # countmap = cv2.bitwise_and(countmap, mapnonzero)
        # countmap = np.clip(countmap, 0, 4)

        # bluemap = newbase
        # libimg.show(bluemap)



        # # # libimg.show(mapMask)
        # # mapMaskInv = 255-mapMask
        # # # libimg.show(mapMaskInv)

        # # bluemapSame = cv2.bitwise_and(bluemap, mapMaskInv)
        # # bluemapChange = cv2.bitwise_and(bluemap, mapMask)
        # # bluemapChange = cv2.addWeighted(bluemapChange, 0.5, map, 0.5, 0)
        # # # bluemapNew = cv2.bitwise_and(map, mapMask)

        # # bluemap = bluemapSame + bluemapChange
        # # # bluemap = bluemapSame + bluemapNew
        # # libimg.show(bluemap)


        # # bluemap = cv2.bitwise_and(bluemap, mapMaskInv)
        # # libimg.show(bluemap)
        # # bluemap = bluemap + map
        # # libimg.show(bluemap)


        # # if nfile>0:
        # # if nfile>3:
        # # if nfile>5:
        # if nfile>8:
        #     sys.exit(0)


    fPositions.close()
    fFiles.close()

    print


if __name__ == '__main__':
    os.chdir('..')
    vgMap(5101)
    print 'done'

