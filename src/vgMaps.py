
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
    
    
    #. loop through these, save each file to stepxx_maps/map-Jupiter-Voyager1.jpg etc
    #. each should have azimuth and elevation
    #. crop each file when done to a square
    #. vg titles could use these for titlepage for each system flyby
    #. use futura font
    
    # Voyager 1
    
    bodies = ['Jupiter', 'Voyager 1', 'Io', 'Europa', 'Ganymede', 'Callisto']
    utcClosest = "1979-03-05"
    ndays = 5
    
    # bodies = ['Saturn','Voyager 1','Titan','Enceladus','Rhea','Mimas','Tethys','Dione']
    # utcClosest = "1980-11-12"
    # ndays = 3
    
    # Voyager 2
    
    # bodies = ['Jupiter', 'Voyager 2', 'Io', 'Europa', 'Ganymede', 'Callisto']
    # utcClosest = "1979-07-09"
    # ndays = 5
    
    # bodies = ['Saturn','Voyager 2','Titan','Enceladus','Rhea','Mimas','Tethys','Dione']
    # utcClosest = "1981-08-25"
    # ndays = 3
    
    # bodies = ['Uranus','Voyager 2','Ariel','Miranda','Oberon','Titania','Umbriel']
    # utcClosest = "1986-01-24"
    # ndays = 3
    
    # bodies = ['Neptune','Voyager 2','Triton']
    # utcClosest = "1989-08-25"
    # ndays = 1
    
    planet = bodies[0]
    observer = bodies[1]
    
    nsteps = 100 # plot density
    
    # get ephemeris time around closest approach (seconds since J2000)
    etClosest = int(spice.str2et(utcClosest))
    etStart = int(etClosest - ndays * 24*60*60 / 2)
    etEnd = int(etClosest + ndays * 24*60*60 / 2)
    etStep = int((etEnd - etStart) / nsteps)
    
    ets = []
    positions = []
    minDist = {}
    minPos = {}
    
    for body in bodies:
        minDist[body] = 9e15
        
    # loop over time range, get positions
    for et in xrange(etStart, etEnd, etStep):
        row = []
        for body in bodies:
            # get position of body (voyager or moon) relative to planet (eg Jupiter).
            # position is an (x,y,z) coordinate in the given frame of reference.
            position, lightTime = spice.spkpos(planet, et, frame, abberationCorrection, body)

            # save time and position to arrays
            ets.append(et)
            row.append(position)
            
            # find closest approach of voyager to each body
            if body==observer: # voyager
                posVoyager = position # save for other bodies
                distance = int(libspice.getDistance(position))
                if distance < minDist[body]:
                    minDist[body] = distance
                    minPos[body] = position
            elif body==planet:
                pass
            else:
                # get distance to voyager, km
                posToVoyager = position-posVoyager
                distance = int(libspice.getDistance(posToVoyager))
                if distance < minDist[body]:
                    minDist[body] = distance
                    minPos[body] = position
        positions.append(row)
        
    # Clean up the kernels
    spice.kclear()

    
    # plot the map

    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    import matplotlib.pyplot as plt

    mpl.rcParams['legend.fontsize'] = 10

    fig = plt.figure()
    ax = fig.gca(projection='3d',axisbg='0.05')
    
    # title = observer + ' at ' + planet
    # ax.set_title(title,color='w')
    
    # colors = ['r','r','g','b','y','c','m']
    # colors = ['r','g','0.7','0.7','0.7','0.7','0.7']
    colors = ['r','g','b','b','b','b','b','b','b']
    
    dots = []
    dotlabels = []
    
    # draw planet
    color = colors[0]
    dot, = ax.plot([0],[0],[0],color+'o',label=bodies[0])
    dots.append(dot)
    dotlabels.append(bodies[0])
    
    i = 0
    for body in bodies:
        rows = [row[i] for row in positions]
        x = [row[0] for row in rows]
        y = [row[1] for row in rows]
        z = [row[2] for row in rows]
        linestyle = 'dotted' if body==observer else 'solid'
        ax.plot(x, y, z, color='0.3', linestyle=linestyle, label=body)
        
        # draw a dot for moon at closest approach
        try:
            pos = minPos[body]
            x = [pos[0]]
            y = [pos[1]]
            z = [pos[2]]
            color = colors[i]
            dot, = ax.plot(x,y,z,color=color, marker='o',label=body)
            dots.append(dot)
            dotlabels.append(body)
        except:
            pass
        
        i += 1

    # add legend
    # eh
    # plt.legend(dots, dotlabels, numpoints=1)
        
    # label axes
    # ax.set_xlabel('x')
    # ax.set_ylabel('y')
    # ax.set_zlabel('z')
    
    # make it a cube
    lim = 1e6 # 1 million km
    ax.set_xlim([-lim,lim])
    ax.set_ylim([-lim,lim])
    ax.set_zlim([-lim,lim])
    
    # label planet, voyager, moons
    offset = int(2 * lim / 100)
    fontsize = 12
    ax.text(offset,offset,offset,planet,size=fontsize,color='w')
    for key in minPos:
        pos = minPos[key]
        x = pos[0]
        y = pos[1]
        z = pos[2]
        ax.text(x+offset,y+offset,z+offset,key,size=fontsize,color='w')
    
    # draw an arrow at end of voyager's trajectory to indicate direction
    # from stackoverflow
    from matplotlib.patches import FancyArrowPatch
    from mpl_toolkits.mplot3d import proj3d
    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
            self._verts3d = xs, ys, zs
        def draw(self, renderer):
            xs3d, ys3d, zs3d = self._verts3d
            xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
            self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
            FancyArrowPatch.draw(self, renderer)
    i = 1 # voyager
    rows = [row[i] for row in positions]
    x = [row[0] for row in rows]
    y = [row[1] for row in rows]
    z = [row[2] for row in rows]
    dx=[x[-2],x[-1]]
    dy=[y[-2],y[-1]]
    dz=[z[-2],z[-1]]
    a = Arrow3D(dx,dy,dz, mutation_scale=20, lw=1, arrowstyle="-|>", color="w")
    ax.add_artist(a)
    
    #. each system will have its own
    ax.view_init(azim=-23, elev=56)
    
    plt.axis('off')
    
    # save image without white border
    # see http://stackoverflow.com/questions/11837979/
    #     removing-white-space-around-a-saved-image-in-matplotlib
    # plt.savefig("map.png", bbox_inches='tight', pad_inches=0.0)
    
    plt.show()
    
    

if __name__ == '__main__':
    os.chdir('..')
    vgMaps()
    print 'done'


