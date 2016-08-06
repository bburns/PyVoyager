
"""
vg init positions command

Initialize positions.csv.
Used to determine expected angular size of targets.

eg
imageId,distance(km),imageSize
C1460413,490003313,0.00145
C1461430,489196322,0.00133
C1462321,489122642,0.03864
C1462323,489120468,0.03864
C1462325,489118422,0.03864
C1462327,489116291,0.03864
C1462329,489114116,0.03864

imageFraction is the fraction of the image width and height (since they're the same)
taken up by the target, eg 0.73

To use, need SPICE kernels - download the following files and put them in the /kernels folder:

ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls
ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/jup100.bsp
ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/sat132.bsp
ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/ura083.bsp
ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/nep016-6.bsp
ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00010.tpc
ftp://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp
ftp://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/spk/Voyager_2.m05016u.merged.bsp
"""

import os
import os.path
import math
import spiceypy as spice

import config
import lib
import libimg
import libspice


def vgInitPositions():
    "Initialize positions.csv with distances to targets for all images in files.csv"

    # open files.csv for reading
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)

    # open positions.csv for writing
    csvPositions, fPositions = lib.openCsvWriter(config.positionsdb)
    fields = 'imageId,distance(km),imageFraction'.split(',') # keep in synch with below
    csvPositions.writerow(fields)

    # load SPICE kernels (data files)
    # see above for sources
    spice.furnsh('kernels/naif0012.tls') # leap second data (5kb)
    spice.furnsh('kernels/Voyager_1.a54206u_V0.2_merged.bsp') # voyager 1 data (6mb)
    spice.furnsh('kernels/Voyager_2.m05016u.merged.bsp') # voyager 2 data (6mb)
    spice.furnsh('kernels/jup100.bsp') # jupiter satellite data (20mb)
    spice.furnsh('kernels/sat132.bsp') # saturn satellite data (63mb)
    spice.furnsh('kernels/ura083.bsp') # uranus satellite data (81mb)
    spice.furnsh('kernels/nep016-6.bsp') # neptune satellite data (9mb)
    spice.furnsh('kernels/pck00010.tpc') # planetary constants (radius etc) (120kb)

    # read db into memory
    targetInfo = lib.readCsv(config.retargetingdb) # remapping listed targets

    # iterate over all available files
    for row in csvFiles:
        # get field values
        # volume,fileid,phase,craft,target,time,instrument,filter,note
        fileId = row[config.filesColFileId] # eg C1385455
        craft = row[config.filesColCraft] # eg Voyager1
        target = row[config.filesColTarget] # eg Io
        utcTime = row[config.filesColTime] # eg 1978-12-11T01:03:29
        instrument = row[config.filesColInstrument] # eg Narrow

        # relabel target field if necessary
        target = lib.retarget(targetInfo, fileId, target)

        # there are a dozen or so UNKNOWN times, all Dark targets, but for one Rhea record
        if utcTime[0]=='U': # UNKNOWN or UNK
            pass
        else:
            # get position of observer (eg Voyager 1) relative to target (eg Io).
            # position is an (x,y,z) coordinate in the given frame of reference.
            ephemerisTime = spice.str2et(utcTime) # seconds since J2000
            observer = craft[:-1] + ' ' + craft[-1] # eg Voyager 1
            frame = 'J2000'
            abberationCorrection = 'NONE'
            doCenter = True
            try:
                position, lightTime = spice.spkpos(target, ephemerisTime, frame,
                                                   abberationCorrection, observer)
            except:
                if target in config.centerTargets:
                    doCenter = True
                elif target in config.dontCenterTargets:
                    doCenter = False
                else:
                    print 'Insufficient data for', target, utcTime

            if doCenter:
                # get distance to target, km
                distance = int(libspice.getDistance(position))

                # get radius of target, km
                # see http://spiceypy.readthedocs.io/en/master/documentation.html
                try:
                    dim, radii = spice.bodvrd(target, 'RADII', 3)
                    radius = int(sum(radii)/3) # just get the avg radius
                except:
                    # if we don't know the radius of the object, just write a 0.0 imageSize
                    radius = 0

                # get angular size of target, degrees
                # sin(angle/2) = radius/distance
                # angle = 2*arcsin(radius/distance)
                angularSize = 2*math.asin(float(radius)/distance) * 180/math.pi

                # get field of view of camera, degrees
                cameraFOV = config.cameraFOVs[instrument] # Narrow -> 0.424 or Wide -> 3.169

                # get size of target relative to the camera fov, dimensionless
                imageSize = angularSize/cameraFOV # 1.0 = full frame
                imageSize = int(imageSize*100000)/100000.0 # trim down

                # write data
                # keep in synch with fields, above
                row = [fileId,distance,imageSize]
                # print row
                csvPositions.writerow(row)

    # Clean up the kernels
    spice.kclear()

    fFiles.close()
    fPositions.close()


if __name__ == '__main__':
    os.chdir('..')
    vgInitPositions()
    print 'done'


