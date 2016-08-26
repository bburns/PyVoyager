
"""
vg maps command
make spice maps of flybys

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


def vgMaps():
    ""

    # load SPICE kernels (data files)
    # see above for sources
    spice.furnsh('kernels/naif0012.tls') # leap second data (5kb)
    spice.furnsh('kernels/Voyager_1.a54206u_V0.2_merged.bsp') # voyager 1 data (6mb)
    spice.furnsh('kernels/Voyager_2.m05016u.merged.bsp') # voyager 2 data (6mb)
    spice.furnsh('kernels/jup100.bsp') # jupiter and satellite data (20mb)
    spice.furnsh('kernels/sat132.bsp') # saturn and satellite data (63mb)
    spice.furnsh('kernels/ura083.bsp') # uranus and satellite data (81mb)
    spice.furnsh('kernels/nep016-6.bsp') # neptune and satellite data (9mb)
    spice.furnsh('kernels/pck00010.tpc') # planetary constants (radius etc) (120kb)

    
    frame = 'J2000'
    # frame = 'IAU_JUPITER' # frame rotates with planet, so voyager spirals around
    abberationCorrection = 'NONE'
    
    
    # Voyager 1
    
    bodies = ['Jupiter', 'Voyager 1', 'Io', 'Europa', 'Ganymede', 'Callisto']
    utcClosest = "1979-03-05"
    ndays = 5
    
    # bodies = ['Saturn','Voyager 1','Titan','Enceladus','Rhea']
    # utcClosest = "1980-11-12"
    # ndays = 3
    
    # Voyager 2
    
    # bodies = ['Jupiter', 'Voyager 2', 'Io', 'Europa', 'Ganymede', 'Callisto']
    # utcClosest = "1979-07-09"
    # ndays = 5
    
    # bodies = ['Saturn','Voyager 2','Titan','Enceladus','Rhea']
    # utcClosest = "1981-08-25"
    # ndays = 3
    
    # bodies = ['Uranus','Voyager 2','Ariel','Miranda']
    # utcClosest = "1986-01-24"
    # ndays = 3
    
    # bodies = ['Neptune','Voyager 2','Triton']
    # utcClosest = "1989-08-25"
    # ndays = 3
    
    nsteps = 100
    
    planet = bodies[0]
    observer = bodies[1]
    
    
    # get ephemeris time (seconds since J2000)
    etClosest = int(spice.str2et(utcClosest))
    etStart = int(etClosest - ndays * 24*60*60 / 2)
    etEnd = int(etClosest + ndays * 24*60*60 / 2)
    # etStart = int(spice.str2et(utcStart))
    # etEnd = int(spice.str2et(utcEnd))
    etStep = int((etEnd - etStart) / nsteps)
    
    ets = []
    positions = []
    minDist = {}
    minPos = {}
    
    for body in bodies:
        minDist[body] = 9e15
        
        
    for et in xrange(etStart, etEnd, etStep):
        # get position of observer (eg Voyager 1) relative to planet (eg Jupiter).
        # position is an (x,y,z) coordinate in the given frame of reference.
        row = []
        for body in bodies:
            position, lightTime = spice.spkpos(planet, et, frame,
                                                      # abberationCorrection, observer)
                                                      abberationCorrection, body)

            ets.append(et)
            # positionsPlanet.append([0,0,0])
            # positionsVoyage.append(positionVoyager)
            row.append(position)
            if body==bodies[1]: # craft
                posVoyager = position
            # elif body=='Jupiter':
            elif body==bodies[0]: # planet
                pass
            else:
                # get distance to voyager, km
                posToVoyager = position-posVoyager
                distance = int(libspice.getDistance(posToVoyager))
                if distance < minDist[body]:
                    minDist[body] = distance
                    minPos[body] = position
        positions.append(row)


        # print position
        # print distance
        # print et, position, distance
        
    # Clean up the kernels
    spice.kclear()

    
    # plot the map

    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    import matplotlib.pyplot as plt

    mpl.rcParams['legend.fontsize'] = 10

    fig = plt.figure()
    # ax = fig.gca(projection='3d',axisbg='black')
    ax = fig.gca(projection='3d',axisbg='0.1')
    colors = ['r','r','g','b','y','c','m']
    # colors = ['r','w','#40ff50','#4050ff','y','#ffff00','c']
    i = 0
    # dots = {}
    dots = []
    dotlabels = []
    for body in bodies:
        rows = [row[i] for row in positions]
        x = [row[0] for row in rows]
        y = [row[1] for row in rows]
        z = [row[2] for row in rows]
        ax.plot(x, y, z, '0.2', label=body)
        
        # draw dot at closest approach
        try:
            pos = minPos[body]
            x = [pos[0]]
            y = [pos[1]]
            z = [pos[2]]
            color = colors[i]
            # ax.plot(x,y,z,color+'o')
            dot, = ax.plot(x,y,z,color+'o',label=body)
            dots.append(dot)
            dotlabels.append(body)
        except:
            pass

        i += 1

    # add legend
    # plt.legend(dots, bodies)
    plt.legend(dots, dotlabels)
        
    # draw planet
    ax.plot([0],[0],[0],'ro')
    
    # label axes
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    
    # make it a cube
    lim = 1e6
    ax.set_xlim([-lim,lim])
    ax.set_ylim([-lim,lim])
    ax.set_zlim([-lim,lim])
    
    # ax.legend()

    plt.axis('off')
    
    # save image without white border
    # see http://stackoverflow.com/questions/11837979/
    #     removing-white-space-around-a-saved-image-in-matplotlib
    plt.savefig("map.png", bbox_inches='tight', pad_inches=0.0)
    
    plt.show()
    
    

if __name__ == '__main__':
    os.chdir('..')
    vgMaps()
    print 'done'


