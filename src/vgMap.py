
"""
vg map command

Build up 2d color maps of targets

kernels from
http://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/ck/vgr1_super.bc
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
    spice.furnsh('kernels/vgr1_super.bc') # voyager 1 pointing data, continuous (11mb)
    spice.furnsh('kernels/vg100019.tsc') # voyager 1 clock data (76kb)
    spice.furnsh('kernels/naif0012.tls') # leap second data (5kb)
    spice.furnsh('kernels/Voyager_1.a54206u_V0.2_merged.bsp') # voyager 1 position data (6mb)
    # spice.furnsh('kernels/Voyager_2.m05016u.merged.bsp') # voyager 2 position data (6mb)
    spice.furnsh('kernels/jup100.bsp') # jupiter and satellite position data (20mb)
    # spice.furnsh('kernels/sat132.bsp') # saturn and satellite position data (63mb)
    # spice.furnsh('kernels/ura083.bsp') # uranus and satellite position data (81mb)
    # spice.furnsh('kernels/nep016-6.bsp') # neptune and satellite position data (9mb)
    spice.furnsh('kernels/pck00010.tpc') # planetary constants (radii etc) (120kb)
    spice.furnsh('kernels/vg1_issna_v02.ti') # instrument data (2kb)
    spice.furnsh('kernels/vg1_isswa_v01.ti') # instrument data (2kb)
    spice.furnsh('kernels/vg2_issna_v02.ti') # instrument data (2kb)
    spice.furnsh('kernels/vg2_isswa_v01.ti') # instrument data (2kb)
    spice.furnsh('kernels/vg1_v02.tf') # voyager 1 frames (12kb)
    spice.furnsh('kernels/vg2_v02.tf') # voyager 2 frames (12kb)

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
    

    camera = 'VG1_ISSNA'
    cameraId, found = spice.bodn2c(camera)
    print camera, cameraId, found
    # spice.getfov(
    stop
    
    
    
    # size of 2d map
    mxmax = 1600
    mymax = 800
    mxcenter = mxmax/2
    mycenter = mymax/2
    
    # set up blank mapping arrays: h(x,y) = (hx(x,y), hy(x,y))
    # h tells map where to pull its pixels from - ie map(mx,my) = im(h(mx,my))
    hx = np.zeros((mymax,mxmax),np.float32)
    hy = np.zeros((mymax,mxmax),np.float32)

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
        if fileId < 'C1462331': continue # blownout images
        if filter != 'Blue': continue # just one filter for now
        
        # get filename
        infile = lib.getFilepath('center', volume, fileId, filter)
        if not os.path.isfile(infile):
            print 'warning file not found', infile
            continue

        # print 'Volume %s mapping %d: %s      \r' % (volume,nfile,infile),
        # print 'Volume %s mapping %d: %s' % (volume,nfile,infile)
        nfile += 1

        
        
        
        
        
        # get camera pointing matrix
        spacecraft = -31 if craft=='Voyager1' else -32
        instrument = spacecraft * 1000 # spacecraft bus
        instrument = -31100 # scan platform
        # instrument = -31101 # na
        ephemerisTime = spice.str2et(time) # seconds since J2000 (will be negative)
        # sclkch = spice.sce2s(spacecraft, ephemerisTime) # spacecraft clock string
        sclkdp = spice.sce2c(spacecraft, ephemerisTime) # spacecraft clock double
        tolerance = spice.sctiks(spacecraft, "0:00:800") # time tolerance
        frame = 'ECLIPB1950' # coordinate frame
        
        targetId = spice.bodn2c(target) # eg 'Jupiter'->599
        # print target, targetId
        
        print
        
        # get camera pointing matrix
        # C is a transformation matrix from the base frame `frame' to
        # the instrument-fixed frame at the time `clkout'.
        # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/ckgp_c.html
        C, clkout, found = spice.ckgp(instrument, sclkdp, tolerance, frame)
        # C = np.array([[1,0,0],[0,0,1],[0,1,0]],np.float)
        # C = np.eye(3)
        print 'C=camera pointing matrix - transform world to camera coords'
        print C
        
        # get boresight vector
        # this is just the third row of the C-matrix, *per spice docs*
        boresight = C[2]
        print 'boresight pointing vector',boresight
        
        # i think it's C[1] that's really stable - pointing up
        
        # Cinv is the inverse of C, translating from camera frame to world frame - dont need it now
        # Cinv = np.linalg.inv(C)
        # print 'Cinv',Cinv
        # yaxis = Cinv[1]
        
        # get world to target frame matrix
        B = spice.tipbod(frame, targetId, ephemerisTime)
        print 'B=world to body/target frame matrix'
        print B
        
        # get target spin axis
        # the last row of the matrix is the north pole vector, *per spice docs*
        # and it seems correct, as it's nearly 0,0,1
        # bz = B[2]
        bz = np.array([0,0,1])
        print 'bz=north pole spin axis',bz

        # get direction from craft to target
        observer = 'Voyager ' + craft[-1] # eg Voyager 1
        abberationCorrection = 'NONE'
        position, lightTime = spice.spkpos(target, ephemerisTime, frame,
                                           abberationCorrection, observer)
        # position = np.array([-6,7,0])
        print 'target position relative to observer',position
        
        # get distance
        d = libspice.getDistance(position)
        print 'd distance in km',d
        
        # # normalize position vector
        posnormal = position / d
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
        print 'target radius in km', targetRadius
        
        # get north pole location
        # wNP = position + targetRadius * bz
        # print 'wNP=north pole in world coords', wNP
        
        # get camera space coordinate
        # c = np.dot(C, wNP)
        # print 'c=north pole in camera space',c
        c = np.dot(C, position)
        print 'c=position in camera space',c
        
        # get screen coordinate
        print 'f=focal length',f
        cz = c[2]
        fz = f/cz
        print 'fz=f/cz',fz
        S = np.array([[fz,0,0],[0,fz,0]])
        s = np.dot(S, c)
        # ie sx=cx*f/cz; sy=cy*f/cz
        print 's=screen space (-1 to 1)',s
        
        # get image coordinate
        p = s * 800/2.0
        p = p + 400
        print 'p=pixel space (0 to 800)',p
        
        print
        print
        sys.exit(0)
        
        
        # get orientation of target - north pole and meridian
        # ra = north pole right ascension (0 to 2pi?)
        # dec = north pole declination (-pi/2 to pi/2?)
        # pm = location of prime meridian (0 to 2pi?)
        #. this gives you info in J2000 - want it in B1950, or convert those to J2000 also
        # ra, dec, pm, lambda_ = spice.bodeul(targetId, ephemerisTime) #. need this
        # ra = 0
        # dec = math.pi/2 # straight up
        # pm = 0
        # lambda_ = 0        
        # print ra, dec, pm, lambda_
        
        # print
        # stop
        
        # # get expected angular size (as fraction of frame) and radius
        # imageFraction = lib.getImageFraction(csvPositions, fileId)
        # targetRadius = int(400*imageFraction) #.param

        # # read image
        # im = cv2.imread(infile)
        
        # #. draw azimuth on image
        
        
        # libimg.show(im)

        # # build hx,hy arrays, which tell map where to pull pixels from in source image
        # r = targetRadius # pixels
        # for mx in xrange(mxmax/2): # 0 to 800 -> 0 to pi = front half of sphere
        #     for my in xrange(mymax): # 0 to 800
                
        #         # q: map
        #         qx = mx * 2 * math.pi / mxmax # 0 to 2pi
        #         qy = -float(my-mycenter)/mycenter # 1 to -1
                
        #         # p: image
        #         px = -math.sqrt(1 - qy**2) * math.cos(qx) # -1 to 1
        #         py = qy # 1 to -1
                
        #         # s: image
        #         sx = px * r + 400 # 0 to 800
        #         sy = -py * r + 400 # 0 to 800
                
        #         hx[my][mx] = sx
        #         hy[my][mx] = sy
        
        # # do remapping
        # # map = cv2.remap(im, hx, hy, cv2.INTER_LINEAR)
        # # libimg.show(map)

        # #. now need to blend this into the main map
        
        

    fPositions.close()
    fFiles.close()

    print
    

if __name__ == '__main__':
    os.chdir('..')
    vgMap(5101)
    print 'done'

