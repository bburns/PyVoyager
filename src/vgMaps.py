
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


def loadSpice():
    """
    load SPICE kernels (data files)
    see above for sources
    """
    spice.furnsh('kernels/naif0012.tls') # leap second data (5kb)
    spice.furnsh('kernels/Voyager_1.a54206u_V0.2_merged.bsp') # voyager 1 data (6mb)
    spice.furnsh('kernels/Voyager_2.m05016u.merged.bsp') # voyager 2 data (6mb)
    spice.furnsh('kernels/jup100.bsp') # jupiter and satellite data (20mb)
    spice.furnsh('kernels/sat132.bsp') # saturn and satellite data (63mb)
    spice.furnsh('kernels/ura083.bsp') # uranus and satellite data (81mb)
    spice.furnsh('kernels/nep016-6.bsp') # neptune and satellite data (9mb)
    spice.furnsh('kernels/pck00010.tpc') # planetary constants (radius etc) (120kb)



def plotMap(flyby, positions, minPos):

    "plot the map for the given flyby"

    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    import matplotlib.pyplot as plt

    bodies = flyby.bodies
    planet = bodies[0]
    observer = bodies[1]

    title = observer + ' at ' + planet
    # title = observer + ' at ' + planet + ' (' + flyby.date[:4] + ')'
    # axisMax = 1e6 # 1 million km
    axisMax = flyby.axisMax # million km
    bgcolor = '0.05' # grayscale 0-1
    labelsize = 12
    labelcolor = '0.9' # grayscale 0-1
    labeloffset = int(2 * axisMax / 25) # label offset

    # set font etc
    # see http://matplotlib.org/users/customizing.html
    # mpl.rcParams['legend.fontsize'] = 10
    # mpl.rcParams.update({'font.size': 22})
    mpl.rcParams['font.size'] = 20
    mpl.rcParams['font.family'] = 'Futura-Light'

    #axes.titlesize : large # fontsize of the axes title
    #axes.labelsize : medium # fontsize of the x any y labels
    #xtick.labelsize : medium # fontsize of the tick labels
    #legend.fontsize : large
    #figure.dpi : 80 # figure dots per inch
    mpl.rcParams['figure.dpi'] = 80 # figure dots per inch
    mpl.rcParams['figure.figsize'] = (8,8) # figure size in inches
    mpl.rcParams['figure.edgecolor'] = 'black' # figure edgecolor

    mpl.rcParams['savefig.edgecolor'] = 'black' # figure edgecolor when saving
    mpl.rcParams['savefig.dpi'] = 125
    #savefig.facecolor   : white    # figure facecolor when saving

    fig = plt.figure()
    ax = fig.gca(projection='3d',axisbg=bgcolor)

    ax.set_title(title,color='w')

    # color of bodies, in order
    moon = '#ff8000'
    colors = ['r','g',moon,moon,moon,moon,moon,moon,moon]

    dots = []
    dotlabels = []

    # draw planet
    color = colors[0]
    dot, = ax.plot([0],[0],[0],color+'o')
    dots.append(dot)
    dotlabels.append(bodies[0])

    # draw orbit lines and voyager path
    i = 0
    for body in bodies:
        rows = [row[i] for row in positions]
        x = [row[0] for row in rows]
        y = [row[1] for row in rows]
        z = [row[2] for row in rows]

        # draw line
        linestyle = 'dotted' if body==observer else 'solid'
        ax.plot(x, y, z, color='0.3', linestyle=linestyle)

        # draw a dot for moon at closest approach
        try:
            pos = minPos[body]
            x = [pos[0]]
            y = [pos[1]]
            z = [pos[2]]
            color = colors[i]
            dot, = ax.plot(x,y,z,color=color, marker='o')
            dots.append(dot)
            dotlabels.append(body)
        except:
            pass

        i += 1

    # add legend
    # plt.legend(dots, dotlabels, numpoints=1)

    # label axes
    # ax.set_xlabel('x')
    # ax.set_ylabel('y')
    # ax.set_zlabel('z')

    # make it a cube
    ax.set_xlim([-axisMax,axisMax])
    ax.set_ylim([-axisMax,axisMax])
    ax.set_zlim([-axisMax,axisMax])

    # label planet, voyager, moons
    # labelcolor = 'w'
    ax.text(labeloffset,labeloffset,labeloffset,planet,size=labelsize,color=labelcolor)
    for key in minPos:
        pos = minPos[key]
        x = pos[0]
        y = pos[1]
        z = pos[2]
        ax.text(x+labeloffset,y+labeloffset,z+labeloffset,key,size=labelsize,color=labelcolor)

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

    # each system will have its own view
    azim, elev = flyby.azimuthElevation
    ax.view_init(azim=azim, elev=elev)

    # no axes
    plt.axis('off')

    # save image without white border
    # see http://stackoverflow.com/questions/11837979/
    #     removing-white-space-around-a-saved-image-in-matplotlib
    filename = 'map-' + planet + '-' + observer.replace(' ','') + '.png'
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.0)

    # plt.show()


def vgMaps():
    
    "create maps for each system flyby"

    loadSpice()

    #. loop through these, save each file to stepxx_maps/map-Jupiter-Voyager1.jpg etc
    #. crop each file when done to a square
    #. vg titles could use these for titlepage for each system flyby
    #. might as well draw info on maps here - Voyager 1 at Jupiter, date, etc - futura font


    # note: azimuthElevation values were determined with the plot viewer
    class Flyby:
        bodies = None
        date = None
        ndays = None
        azimuthElevation = None

    flybys = []

    flyby = Flyby()
    flyby.bodies = ['Jupiter', 'Voyager 1', 'Io', 'Europa', 'Ganymede', 'Callisto']
    flyby.date = "1979-03-05"
    flyby.ndays = 4
    flyby.axisMax = 1.2e6 # km
    flyby.azimuthElevation = (46,101)
    flybys.append(flyby)

    flyby = Flyby()
    flyby.bodies = ['Saturn', 'Voyager 1','Titan','Enceladus','Rhea','Mimas','Tethys','Dione']
    flyby.date = "1980-11-12"
    flyby.ndays = 3
    flyby.axisMax = 0.8e6 # km
    flyby.azimuthElevation = (80,97)
    flybys.append(flyby)

    flyby = Flyby()
    flyby.bodies = ['Jupiter', 'Voyager 2', 'Io', 'Europa', 'Ganymede', 'Callisto']
    flyby.date = "1979-07-09"
    flyby.ndays = 5
    flyby.axisMax = 1e6 # km
    flyby.azimuthElevation = (102,107)
    flybys.append(flyby)

    flyby = Flyby()
    flyby.bodies = ['Saturn','Voyager 2','Titan','Enceladus','Rhea','Mimas','Tethys','Dione']
    flyby.date = "1981-08-26"
    flyby.ndays = 2
    flyby.axisMax = 0.7e6 # km
    flyby.azimuthElevation = (172,82)
    flybys.append(flyby)

    flyby = Flyby()
    flyby.bodies = ['Uranus','Voyager 2','Ariel','Miranda','Oberon','Titania','Umbriel']
    flyby.date = "1986-01-25"
    flyby.ndays = 2
    flyby.axisMax = 0.4e6 # km
    flyby.azimuthElevation = (-82,-7)
    flybys.append(flyby)

    flyby = Flyby()
    flyby.bodies = ['Neptune','Voyager 2','Triton'] # proteus not in kernels
    flyby.date = "1989-08-25"
    flyby.ndays = 2
    flyby.axisMax = 1e6 # km
    flyby.azimuthElevation = (-62,40)
    flybys.append(flyby)


    for flyby in flybys:

        planet = flyby.bodies[0]
        observer = flyby.bodies[1]

        nsteps = 100 # plot density

        # get ephemeris time around closest approach (seconds since J2000)
        etClosest = int(spice.str2et(flyby.date))
        etStart = int(etClosest - flyby.ndays * 24*60*60 / 2)
        etEnd = int(etClosest + flyby.ndays * 24*60*60 / 2)
        etStep = int((etEnd - etStart) / nsteps)

        # initialize data structs
        ets = []
        positions = []
        minDist = {}
        minPos = {}
        for body in flyby.bodies:
            minDist[body] = 9e15

        # loop over time range, get positions
        for et in xrange(etStart, etEnd, etStep):
            row = []
            for body in flyby.bodies:
                # get position of body (voyager or moon) relative to planet (eg Jupiter).
                # position is an (x,y,z) coordinate in the given frame of reference.
                frame = 'J2000'
                abberationCorrection = 'NONE'
                position, lightTime = spice.spkpos(planet, et, frame, abberationCorrection, body)

                # save time and position to arrays
                ets.append(et)
                row.append(position)

                # find closest approach of voyager to each body
                if body==observer: # voyager
                    posVoyager = position # save for other bodies
                    # distance = int(libspice.getDistance(position))
                    # if distance < minDist[body]:
                        # minDist[body] = distance
                        # minPos[body] = position
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

        # make the map
        plotMap(flyby, positions, minPos)

    # all done - clean up the kernels
    spice.kclear()


if __name__ == '__main__':
    os.chdir('..')
    vgMaps()
    print 'done'


