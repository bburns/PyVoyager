
"""
vg pages command

Build pages like intro, epilogue, credits
"""

import os
import csv

import config
import lib
import libimg

        

def vgPages():
    "Make special pages"
    
    # note: ffmpeg requires file type to match that of other frames in movie,
    # so use config.extension.

    folderPages = config.folders['pages']
    
    
    # intro
    title = "Voyager: The Grand Tour"
    page = libimg.Page()
    page.vtab(5)
    page.println(title, color=200, center=True)
    filepath = folderPages + 'Intro' + config.extension
    page.save(filepath)

    
    # credits
    page = libimg.Page()
    page.vtab(2)
    page.htab(0)
    page.println("Credits",color=255)
    page.size(32)
    credits = """Images: NASA/JPL
Image processing: Brian Burns
Music: J.S.Bach

img2png, flatfields: Bjorn Jonsson
Software: Python, OpenCV, SciPy, NumPy, SpiceyPy
ECC Maximization: G. D. Evangelidis and E. Z. Psarakis

With thanks to Mark Showalter, seti.org, NAIF,
planetary.org, UnmannedSpacecraft.com.

License: CCSA
Project home page: https://bburns.github.io/PyVoyager
"""
    page.println(credits)
    filepath = folderPages + 'Credits' + config.extension
    page.save(filepath)
    
    
    # epilogue
    page = libimg.Page()
    page.vtab(5)
    page.htab(1)
    # quote = """Dedicated to all future explorers..."""
    quote = """Dedicated to the Voyager team,
and all future explorers..."""
    page.println(quote,color=160,center=True)
    filepath = folderPages + 'Epilogue' + config.extension
    page.save(filepath)


if __name__ == '__main__':
    os.chdir('..')
    vgPages()
    print 'done'
