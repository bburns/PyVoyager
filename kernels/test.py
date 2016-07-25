
# Voyager distance calculations using SPICE and Voyager kernels.
# Uses Python interface - see https://github.com/AndrewAnnex/SpiceyPy

# Instructions:
#   run `pip install spicepy`
# Download
#   ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls
#   ftp://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp
#   ftp://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/spk/Voyager_2.m05016u.merged.bsp



import math
import spiceypy as spice


# utc time range
# utcStart = '1979-03-01'
# utcStart = '1979-01-01'
# utcStop  = '1979-03-10'
utcStart = '1986-01-01'
utcStop  = '1986-01-30'

# target and observer
# target = 'JUPITER BARYCENTER'
# target = 'Ganymede'
# target = 'URANUS'
target = 'URANUS BARYCENTER'
# observer = 'VOYAGER 1'
# observer = 'Voyager 1'
observer = 'VOYAGER 2'


def et2str(et):
    "Convert an ephemeris time (seconds after J2000) to a UTC string."
    # see https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/et2utc_c.html
    formatStr = "ISOC"
    prec = 0
    s = spice.et2utc(et, formatStr, prec, lenout=256)
    return s

def getDistance(x,y,z):
    return math.sqrt(x**2+y**2+z**2)


# load kernels (data files)
spice.furnsh('naif0012.tls') # leap second data
spice.furnsh('Voyager_1.a54206u_V0.2_merged.bsp')
spice.furnsh('Voyager_2.m05016u.merged.bsp')
# spice.furnsh('jup100.bsp') # jupiter satellite data (20mb)

# get ephemeris time (seconds since J2000)
etStart = spice.str2et(utcStart)
etStop = spice.str2et(utcStop)

# get time range
nsteps = 50
etTimes = [i*(etStop-etStart)/nsteps + etStart for i in range(nsteps)]

# get vectors from observer to target
# see http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkpos_c.html
frame = 'J2000'
abcorr = 'NONE' # abberation correction
positions, lightTimes = spice.spkpos(target, etTimes, frame, abcorr, observer)




# # spice.furnsh('kernels/naif0012.tls') # load leap second data
# # spice.furnsh('kernels/Voyager_1.a54206u_V0.2_merged.bsp') # voyager 1 data

# # get field values
# # volume,fileid,phase,craft,target,time,instrument,filter,note
# # volume = row[config.filesColVolume] # eg 5101
# # fileId = row[config.filesColFileId] # eg C1385455
# # phase = row[config.filesColPhase] # eg Jupiter
# # craft = row[config.filesColCraft] # eg Voyager1
# # target = row[config.filesColTarget] # eg Io
# target = 'Jupiter'
# # time = row[config.filesColTime] # eg 1978-12-11T01:03:29
# time = '1978-12-11T01:03:29'
# # instrument = row[config.filesColInstrument] # eg Narrow

# et = spice.str2et(time)
# frame = 'J2000'
# abcorr = 'NONE' # abberation correction
# target = target + ' BARYCENTER'
# observer = 'Voyager 1'
# position, lightTime = spice.spkpos(target, et, frame, abcorr, observer)
# print position
# # distance = getDistance(position)
# # fields = 'volume,imageId,target,distance(km)'.split(',') # keep in synch with row, below
# # row = [volume,fileId,target,distance]
# # print row
# # writer.writerow(row)
# # print distance


# end






# get distances
# distances = [math.sqrt(x**2+y**2+z**2) for x,y,z in positions]
distances = [getDistance(x,y,z) for x,y,z in positions]

# Jupiter has a mean radius of 69,911 kilometers

# Voyager 1's closest approach to Jupiter occurred March 5, 1979
# Distance 349,000 km
# Voyager 2's closest approach to Jupiter occurred on July 9, 1979.
# It came within 570,000 km of the planet's cloud tops.

for i, distance in enumerate(distances):
    print "%s   %.0f" % (et2str(etTimes[i]), distance)

# 1979-03-04T10:04:48   1720452
# 1979-03-04T14:24:00   1482460
# 1979-03-04T18:43:12   1238139
# 1979-03-04T23:02:24   987003
# 1979-03-05T03:21:36   730901
# 1979-03-05T07:40:48   485618
# 1979-03-05T12:00:00   348461
# 1979-03-05T16:19:12   477570
# 1979-03-05T20:38:24   721531
# 1979-03-06T00:57:36   977694
# 1979-03-06T05:16:48   1229137
# 1979-03-06T09:36:00   1473770
# 1979-03-06T13:55:12   1712063

# Clean up the kernels
spice.kclear()



