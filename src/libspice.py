

import math
import spiceypy as spice




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



