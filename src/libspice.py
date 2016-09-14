

import math
import spiceypy as spice



def loadKernels():
    "load SPICE kernels (data files)"
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







def et2str(et):
    "Convert an ephemeris time (seconds after J2000) to a UTC string."
    # see https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/et2utc_c.html
    formatStr = "ISOC"
    prec = 0
    s = spice.et2utc(et, formatStr, prec, lenout=256)
    return s

def getDistance(position):
    x,y,z = position
    return math.sqrt(x**2 + y**2 + z**2)



