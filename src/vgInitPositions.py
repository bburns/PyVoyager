
# vg init positions command
# initialize db/positions.csv
# used to determine angular size of targets

# eg
# volume,imageId,target,distance(km),imageSize
# 5101,C1460413,Ganymede,490003313,0.0014511376269197615
# 5101,C1461430,Callisto,489196322,0.0013314370284606923
# 5101,C1462321,Jupiter,489122642,0.0386484329224622
# 5101,C1462323,Jupiter,489120468,0.0386486047036475
# 5101,C1462325,Jupiter,489118422,0.038648766372156
# 5101,C1462327,Jupiter,489116291,0.03864893475853612
# 5101,C1462329,Jupiter,489114116,0.038649106623201084
# 5101,C1462331,Jupiter,489111963,0.03864927675097021
# 5101,C1462333,Jupiter,489109810,0.03864944688023712


# degrees
# narrowAngleFOV = 0.424
# wideAngleFOV = 3.169
cameraFOVs = {'Narrow': 0.424, 'Wide': 3.169}


import csv
import os
import os.path
import math
import spiceypy as spice

import config
import lib
import libimg
import libspice


def initPositions():
    "calculate distances to targets for all images in db/files.csv"

    # imagespath = lib.getImagespath(volumeNum)
    # imagesfolder = config.imagesFolder + '/' + imageType + '/VGISS_' + str(volumeNum)

    # open positions.csv for writing
    fileout = open(config.positionsdb, 'wb')
    # fields = 'volume,imageId,target,distance(km),imageSize'.split(',') # keep in synch with below
    fields = 'imageId,distance(km),imageSize'.split(',') # keep in synch with below
    writer = csv.writer(fileout)
    writer.writerow(fields)

    # open the files.csv file for reading
    filein = open(config.filesdb, 'rt')
    reader = csv.reader(filein)

    # load spice kernels (data files)
    spice.furnsh('kernels/naif0012.tls') # load leap second data (5kb)
    spice.furnsh('kernels/Voyager_1.a54206u_V0.2_merged.bsp') # voyager 1 data (6mb)
    spice.furnsh('kernels/Voyager_2.m05016u.merged.bsp') # voyager 2 data (6mb)
    spice.furnsh('kernels/jup100.bsp') # jupiter satellite data (20mb)
    spice.furnsh('kernels/sat132.bsp') # saturn satellite data (63mb)
    spice.furnsh('kernels/ura083.bsp') # uranus satellite data (81mb)
    spice.furnsh('kernels/nep016-6.bsp') # neptune satellite data (9mb)
    spice.furnsh('kernels/pck00010.tpc') # planet/moon physical data

    # don't have data for these targets, so will assume they are small enough to center on
    ignoreTargets = 'Dark,Sky,Plaque,Cal_Lamps,Orion,Vega,Star,Pleiades,Scorpius,\
Amalthea,Thebe,J_Rings,Adrastea,Metis,Sigma_Sgr,Larissa,\
System,Beta_Cma,Arcturus,S_Rings,Phoebe,Unk_Sat,Helene,Prometheus,\
Pandora,Calypso,U_Rings,N_Rings,Proteus,Amalthea,Taurus,\
Janus,Telesto,Puck,Theta_Car,Epimetheus'.split(',')

    # iterate over all available files
    i = 0
    for row in reader:
        if row==[] or row[0][0]=="#": continue # skip blank line and comments
        if i==0: fields = row # get column headers
        else:
            # get field values
            # volume,fileid,phase,craft,target,time,instrument,filter,note
            volume = row[config.filesColVolume] # eg 5101
            fileId = row[config.filesColFileId] # eg C1385455
            # phase = row[config.filesColPhase] # eg Jupiter
            craft = row[config.filesColCraft] # eg Voyager1
            target = row[config.filesColTarget] # eg Io
            time = row[config.filesColTime] # eg 1978-12-11T01:03:29
            instrument = row[config.filesColInstrument] # eg Narrow

            if time=='UNKNOWN' or time=='UNK':
                pass
            else:
                et = spice.str2et(time)
                frame = 'J2000'
                abcorr = 'NONE' # abberation correction
                observer = craft[:-1] + ' ' + craft[-1] # eg Voyager 1
                try:
                    position, lightTime = spice.spkpos(target, et, frame, abcorr, observer)
                except:
                    if not target in ignoreTargets:
                        print 'Insufficient data for', target, time
                else:
                    # get distance to target
                    distance = int(libspice.getDistance(position))

                    # get radius of target
                    # see  http://spiceypy.readthedocs.io/en/master/documentation.html
                    dim, radii = spice.bodvrd(target, 'RADII', 3)
                    radius = int(sum(radii)/3) # just get the avg radius

                    # get angular size of target
                    # sin(angle/2) = radius/distance
                    # angle = 2*arcsin(radius/distance)
                    angularSize = 2*math.asin(float(radius)/distance) * 180/math.pi

                    # get field of view of camera
                    cameraFOV = cameraFOVs[instrument] # Narrow -> 0.424 or Wide -> 3.169

                    # get size of target relative to the camera fov
                    imageSize = angularSize/cameraFOV # 1.0 = full frame
                    imageSize = int(imageSize*100000)/100000.0 # trim down

                    # keep in synch with fields, above
                    # row = [volume,fileId,target,distance]
                    # row = [volume,fileId,target,distance,radius,angularSize,imageSize]
                    # row = [volume,fileId,target,distance,imageSize]
                    row = [fileId,distance,imageSize]
                    # print row

                    writer.writerow(row)

        i += 1

    # Clean up the kernels
    spice.kclear()

    filein.close()
    fileout.close()



if __name__ == '__main__':
    os.chdir('..')
    initPositions()
    print 'done'




