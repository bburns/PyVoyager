
# build title pages for different targets

import os
import csv

import config
import lib


title = target + " Flyby"
subtitle1 = camera + "-Angle Camera"
subtitle2 = planet + " System"
subtitle3 = "Voyager " + spacecraft[-1:]

img = lib.makeTitlePage(title, subtitle1, subtitle2, subtitle3)

filename = "foo.png"
img.save(filename)

import os
os.system(filename)

