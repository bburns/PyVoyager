
"""
vg map command

Build up 2d color maps of targets

kernels from
# http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/ck/vgr1_super.bc
http://pds-rings.seti.org/voyager/ck/vg1_jup_version1_type1_iss_sedr.bc
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/sclk/vg100019.tsc
http://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls
http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/jup100.bsp
http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/sat132.bsp
http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/ura083.bsp
http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/nep016-6.bsp
http://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00010.tpc
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/spk/Voyager_2.m05016u.merged.bsp
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/ik/vg1_issna_v02.ti
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/ik/vg1_isswa_v01.ti
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/ik/vg2_issna_v02.ti
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/ik/vg2_isswa_v01.ti
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/fk/vg1_v02.tf
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/fk/vg2_v02.tf
"""

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


#. handle targetpath
def vgMap(filterVolumes=None, optionOverwrite=False, directCall=True):
# def vgMap(filterVolumes=None, filterTargetPath='', optionOverwrite=False, directCall=True):
    
    "Build up 2d color map"

    # if filterVolume:
        # filterVolume = str(filterVolume)
        
    # outputSubfolder = lib.getSubfolder('map', filterVolume)

    # create folder
    # lib.mkdir(outputSubfolder)

    # load SPICE kernels (data files)
    # see above for sources
    # spice.furnsh('kernels/vgr1_super.bc') # voyager 1 pointing data, continuous (11mb)
    spice.furnsh('kernels/ck/vg1_jup_version1_type1_iss_sedr.bc') # voyager 1 jupiter pointing, discrete (700kb)
    spice.furnsh('kernels/sclk/vg100019.tsc') # voyager 1 clock data (76kb)
    spice.furnsh('kernels/lsk/naif0012.tls') # leap second data (5kb)
    spice.furnsh('kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp') # voyager 1 position data (6mb)
    # spice.furnsh('kernels/spk/Voyager_2.m05016u.merged.bsp') # voyager 2 position data (6mb)
    spice.furnsh('kernels/spk/jup100.bsp') # jupiter and satellite position data (20mb)
    # spice.furnsh('kernels/spk/sat132.bsp') # saturn and satellite position data (63mb)
    # spice.furnsh('kernels/spk/ura083.bsp') # uranus and satellite position data (81mb)
    # spice.furnsh('kernels/spk/nep016-6.bsp') # neptune and satellite position data (9mb)
    spice.furnsh('kernels/pck/pck00010.tpc') # planetary constants (radii etc) (120kb)
    spice.furnsh('kernels/ik/vg1_issna_v02.ti') # instrument data (2kb)
    spice.furnsh('kernels/ik/vg1_isswa_v01.ti') # instrument data (2kb)
    spice.furnsh('kernels/ik/vg2_issna_v02.ti') # instrument data (2kb)
    spice.furnsh('kernels/ik/vg2_isswa_v01.ti') # instrument data (2kb)
    spice.furnsh('kernels/fk/vg1_v02.tf') # voyager 1 frames (12kb)
    spice.furnsh('kernels/fk/vg2_v02.tf') # voyager 2 frames (12kb)

    # read small dbs into memory
    # centeringInfo = lib.readCsv(config.dbCentering) # when to turn centering on/off
    retargetingInfo = lib.readCsv(config.dbRetargeting) # remapping listed targets

    # open positions.csv file for target angular size info
    csvPositions, fPositions = lib.openCsvReader(config.dbPositions)

    # # open centers_new.csv file to write any new records to
    # csvNewCenters, fNewCenters = lib.openCsvWriter(config.dbCentersNew)

    # # dictionary to keep track of last image file in target sequence (eg for Ariel flyby)
    # lastImageInTargetSequence = {}
    
    #. use ik
    # cameraFOVs = {'Narrow': 0.424, 'Wide': 3.169}
    fov = config.cameraFOVs['Narrow'] * math.pi / 180
    # fov = config.cameraFOVs['Wide'] * math.pi / 180
    f = 1.0 / math.tan(fov/2)
    # f = 1.0
    
    # print help(spice.bodn2c)

    # camera = 'VG1_ISSNA'
    # cameraId = spice.bodn2c(camera)
    # print camera, cameraId, found
    cameraId = -31101
    # print help(spice.getfov)
    # shape, dref, bsight, n, bounds = spice.getfov(cameraId, 4, 20,20)
    shape, cameraName, cameraBoresight, nbounds, bounds = spice.getfov(cameraId, 4)
    # print shape, cameraName, cameraBoresight, nbounds, bounds
    # RECTANGLE VG1_ISSNA [ 0.  0.  1.] 4 [[ 0.0037001  0.0037001  1.       ]
    #  [-0.0037001  0.0037001  1.       ]
    #  [-0.0037001 -0.0037001  1.       ]
    #  [ 0.0037001 -0.0037001  1.       ]]
    
    
    # size of 2d map
    # mxmax = 1600
    # mymax = 800
    # mxmax = 800
    # mymax = 400
    mxmax = config.imsize
    mymax = config.imsize/2
    mxcenter = mxmax/2
    mycenter = mymax/2
    
    # set up blank mapping arrays: h(x,y) = (hx(x,y), hy(x,y))
    # h tells map where to pull its pixels from - ie map(mx,my) = im(h(mx,my))
    hx = np.zeros((mymax,mxmax),np.float32)
    hy = np.zeros((mymax,mxmax),np.float32)

    # make blank maps for each color channel
    # bluemap = np.zeros((mymax,mxmax),np.float32)
    bluemap = np.zeros((mymax,mxmax),np.uint8)
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
        if target!='Jupiter': continue
        if fileId < 'C1462335': continue # blownout images
        if filter != 'Blue': continue # just one filter for now
        
        # get filename
        infile = lib.getFilepath('center', volume, fileId, filter)
        # infile = lib.getFilepath('adjust', volume, fileId, filter)
        if not os.path.isfile(infile):
            print 'warning file not found', infile
            continue

        # print 'Volume %s mapping %d: %s      \r' % (volume,nfile,infile),
        # print 'Volume %s mapping %d: %s' % (volume,nfile,infile)
        nfile += 1

        
        # get target code
        targetId = spice.bodn2c(target) # eg 'Jupiter'->599
        # print target, targetId
        
        # get instrument        
        spacecraft = -31 if craft=='Voyager1' else -32
        spacecraftBus = spacecraft * 1000
        spacecraftScanPlatform = spacecraftBus - 100
        spacecraftNarrowCamera = spacecraftScanPlatform - 1
        spacecraftWideCamera = spacecraftScanPlatform - 2
        # instrument = spacecraft * 1000 # spacecraft bus - use for NAIF continuous kernels
        # instrument = -31100 # scan platform - use for PDS discrete kernels
        # instrument = -31101 # na
        # instrument = spacecraftBus # use for NAIF continuous kernels
        instrument = spacecraftScanPlatform # use for PDS discrete kernels
        
        # get ephemeris time
        ephemerisTime = spice.str2et(time) # seconds since J2000 (will be negative)
        # sclkch = spice.sce2s(spacecraft, ephemerisTime) # spacecraft clock string
        sclkdp = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock double
        print 'sclkdp',sclkdp
        tolerance = spice.sctiks(spacecraft, "0:00:800") # time tolerance
        frame = 'ECLIPB1950' # coordinate frame
        # frame = 'J2000' # coordinate frame
        
        print
        
        # get camera pointing matrix
        # C is a transformation matrix from the base frame `frame' to
        # the instrument-fixed frame at the time `clkout'.
        # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/ckgp_c.html
        C, clkout, found = spice.ckgp(instrument, sclkdp, tolerance, frame)
        print 'C=camera pointing matrix - transform world to camera coords'
        print C
        
        # get boresight vector
        # this is just the third row of the C-matrix, *per spice docs*
        boresight = C[2]
        print 'boresight pointing vector',boresight
        
        
        # get world to target frame matrix
        B = spice.tipbod(frame, targetId, ephemerisTime)
        print 'B=world to body/target frame matrix'
        print B
        
        # get target spin axis
        # the last row of the matrix is the north pole vector, *per spice docs*
        # seems correct, as it's nearly 0,0,1
        bz = B[2]
        print 'bz=north pole spin axis',bz
        print
        
        # get location of prime meridian
        rotationRate = 870.5366420 # deg/day
        primeMeridian = rotationRate /24/60/60 * ephemerisTime # deg
        print 'primeMeridian (deg)', primeMeridian % 360
        # rotationRateRadiansPerSec = rotationRateDegPerDay * math.pi/180 /24/60/60
        # primeMeridianRadians = rotationRateRadiansPerSec * ephemerisTime % math.pi*2
        primeMeridianRadians = primeMeridian * math.pi/180
        
        # get target position
        # direction from craft to target
        observer = 'Voyager ' + craft[-1] # eg Voyager 1
        abberationCorrection = 'NONE'
        frame = 'ECLIPB1950' # coordinate frame
        # print target, observer, ephemerisTime
        position, lightTime = spice.spkpos(target, ephemerisTime, frame,
                                           abberationCorrection, observer)
        # position = np.array([-63,78,1])
        # position = np.array([-1,1,0])
        # position = np.array([-1,1.2,.1])
        # position = np.array([.1,100,0])
        print 'target position relative to observer',position
        
        # get distance
        distance = libspice.getDistance(position)
        print 'distance in km',distance
        
        # # normalize position vector
        posnormal = position / distance
        print 'position normalized', posnormal
        
        dot = np.dot(boresight, posnormal)
        print 'boresight dot posnormal', dot
        theta = math.acos(dot) * 180/math.pi
        print 'angle between boresight and position', theta
        
        
        # get target information
        nvalues, radii = spice.bodvrd(target, 'RADII', 3)
        targetRadiusEquator = (radii[0] + radii[1]) / 2
        targetRadiusPoles = radii[2]
        targetRadius = sum(radii) / 3
        flatteningCoefficient = (targetRadiusEquator - targetRadiusPoles) / targetRadiusEquator
        # print 'target radius in km', targetRadius
        
        # get north pole location
        positionNP = position + targetRadius * bz
        print 'positionNP=north pole in world coords', positionNP
        
        print
        
        # get target position in camera space
        c = np.dot(C, position)
        cNP = np.dot(C, positionNP)
        print 'c=position in camera space',c
        print 'cNP=north pole in camera space',cNP
        
        # get screen coordinate
        print 'f=focal length',f
        cz = c[2]
        fz = f/cz
        print 'fz=f/cz',fz
        S = np.array([[fz,0,0],[0,fz,0]])
        s = np.dot(S, c)
        sNP = np.dot(S, cNP)
        # ie sx=cx*f/cz; sy=cy*f/cz
        print 's=screen space (-1 to 1)',s
        print 'sNP=screen space north pole (-1 to 1)',sNP
        
        npDelta = sNP-s
        npRadians = math.atan(npDelta[0]/npDelta[1])
        npAngle = npRadians * 180/math.pi
        print 'npAngle',npAngle
        
        # get image coordinate
        p = -s * config.imsize/2
        p[0] = p[0]+config.imsize/2
        p[1] = p[1]+config.imsize/2
        pNP = -sNP * config.imsize/2
        pNP[0] = pNP[0]+config.imsize/2
        pNP[1] = pNP[1]+config.imsize/2
        print 'p=pixel space (0 to imsize)',p
        print 'pNP=pixel space north pole (0 to imsize)',pNP
        
        
        angularSize = 2*math.asin(float(targetRadius)/distance) * 180/math.pi

        # get field of view of camera, degrees
        cameraFOV = config.cameraFOVs[camera] # Narrow -> 0.424 or Wide -> 3.169

        # get size of target relative to the camera fov, dimensionless
        imageSize = angularSize/cameraFOV # 1.0 = full frame
        imageSize = int(imageSize*100000)/100000.0 # trim down
        print 'angularsize',angularSize
        print 'fov',cameraFOV
        print 'imagesize',imageSize
        
        imagePixels = imageSize * config.imsize
        print 'imagepixels',imagePixels

    
        print
        print
        # sys.exit(0)
        
        
        # get expected angular size (as fraction of frame) and radius
        imageFraction = lib.getImageFraction(csvPositions, fileId)
        targetRadius = int(config.imsize/2*imageFraction) #.param

        # read image
        im = cv2.imread(infile)
        
        # draw north pole on image
        pt1 = tuple([int(x) for x in p])
        pt2 = tuple([int(x) for x in pNP])
        # print pt1
        im = cv2.line(im, pt1, pt2, 128)
        
        
        # libimg.show(im)
        
        # sys.exit(0)
        
        # what longitudes are visible?
        #. get from position of craft
        visibleLongitudesMin = 0
        visibleLongitudesMax = math.pi
        
        # get axial tilt matrix
        cc = math.cos(npRadians)
        ss = math.sin(npRadians)
        mTilt = np.array([[cc,-ss],[ss,cc]])

        # build hx,hy arrays, which tell map where to pull pixels from in source image
        r = targetRadius # pixels
        # m: map (0 to mxmax, 0 to mymax)
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
                px = sx * r + config.imsize/2 # 0 to 800
                py = -sy * r + config.imsize/2 # 0 to 800
                
                # hx[my][mx] = px
                # hy[my][mx] = py
                visible = (qx >= visibleLongitudesMin) and (qx <= visibleLongitudesMax)
                if visible:
                    hx[my][mx] = px
                    hy[my][mx] = py
                else:
                    hx[my][mx] = 0
                    hy[my][mx] = 0
        
        # do remapping
        map = cv2.remap(im, hx, hy, cv2.INTER_LINEAR)
        map = map[:,:,0]
        # map = np.array(map, np.float32)
        libimg.show(map)

        
        #. now need to blend this into the main map for this filter
        
        # print type(map[0][0])
        # print type(bluemap[0][0])
        
        # bluemap = cv2.addWeighted(bluemap, 0.5, map, 0.5, 0)
        
        # ret, countzero = cv2.threshold(countmap, 0,255, cv2.THRESH_BINARY)
        # ret, countone = cv2.threshold(countmap, 0,255, cv2.THRESH_BINARY)
        # countzero = 255-countone
        # ret, mapMask = cv2.threshold(map, 1, 255, cv2.THRESH_BINARY)
        # mapMask = cv2.bitwise_and(countzero, mapMask)
        # c = mapMask & 1
        # countmap += c
        
        # libimg.show(countmap)
        
        # ret, mapnonzero = cv2.threshold(map, 0,1, cv2.THRESH_BINARY)
        ret, mapnonzero = cv2.threshold(map, 1,1, cv2.THRESH_BINARY)
        
        countmapPlusOne = countmap + 1
        countmap2 = countmap + 1-mapnonzero
        base = np.array(bluemap, np.float32)
        # base = base * countmap / countmapPlusOne
        base = base * countmap2 / countmapPlusOne
        newmap = np.array(map, np.float32)
        newmap = newmap / countmapPlusOne
        newbase = base + newmap
        newbase = np.array(newbase, np.uint8)
        
        # increment countmap where map image data exists
        countmap += mapnonzero
        # countmap = cv2.bitwise_and(countmap, mapnonzero)
        countmap = np.clip(countmap, 0, 4)
        
        bluemap = newbase
        libimg.show(bluemap)
        
        
        
        # # libimg.show(mapMask)
        # mapMaskInv = 255-mapMask
        # # libimg.show(mapMaskInv)
        
        # bluemapSame = cv2.bitwise_and(bluemap, mapMaskInv)
        # bluemapChange = cv2.bitwise_and(bluemap, mapMask)
        # bluemapChange = cv2.addWeighted(bluemapChange, 0.5, map, 0.5, 0)
        # # bluemapNew = cv2.bitwise_and(map, mapMask)
        
        # bluemap = bluemapSame + bluemapChange
        # # bluemap = bluemapSame + bluemapNew
        # libimg.show(bluemap)
        
        
        # bluemap = cv2.bitwise_and(bluemap, mapMaskInv)
        # libimg.show(bluemap)
        # bluemap = bluemap + map
        # libimg.show(bluemap)
        
        # if nfile>0:
        # if nfile>3:
        # if nfile>5:
        if nfile>8:
            sys.exit(0)
        

    fPositions.close()
    fFiles.close()

    print
    

if __name__ == '__main__':
    os.chdir('..')
    vgMap(5101)
    print 'done'

