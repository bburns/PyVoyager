
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
    italicfont = config.italicFont

    em = 36/800.0*config.imsize
 
    # intro
# def makeIntro():
    pagename = "Intro"
    title = "Voyager: The Grand Tour"
    page = libimg.Page()
    page.vtab(5)
    page.setfont(fontsize=2*em)
    page.println(title, color=200, center=True)
    filepath = folderPages + pagename + config.extension
    page.save(filepath)

    
    # prologue
    pagename = "Prologue"
    quote = '''"Sailors on a becalmed sea,
we sense the stirring of a breeze."
   ~ Carl Sagan'''
    page = libimg.Page()
    page.setfont(italicfont,1*em)
    page.vtab(8)
    page.println(quote, color=160, center=True)
    filepath = folderPages + pagename + config.extension
    page.save(filepath)
    
    
    # credits
    pagename = "Credits"
    page = libimg.Page()
    page.vtab(2)
    page.htab(0)
    page.println("Credits",color=255)
    page.setfont(fontsize=0.8*em)
    credits = """Images: NASA/JPL
Image processing: Brian Burns
Music: J.S.Bach

img2png, flatfields: Bjorn Jonsson
Software: Python, OpenCV, SciPy, NumPy, SpiceyPy
ORB: E. Rublee, V. Rabaud, K. Konolige, and G. Bradski
ECC Maximization: G. D. Evangelidis and E. Z. Psarakis

With thanks to Mark Showalter, seti.org, NAIF,
planetary.org, UnmannedSpacecraft.com.

License: CCSA
Project home page: https://bburns.github.io/PyVoyager
"""
    page.println(credits)
    filepath = folderPages + pagename + config.extension
    page.save(filepath)
    
    
    #. add this below palebluedot image
    pagename = "Epilogue"
    page = libimg.Page()
    page.setfont(italicfont,1*em)
    page.vtab(8)
    page.htab(1)
    quote = '''"Our remote descendants, safely arrayed on many 
worlds through the solar system and beyond, will gaze up,
and strain to find the blue dot in their skies. They will
marvel at how vulnerable the repository of raw potential
once was. How perilous, our infancy. How humble, our beginnings.
How many rivers we had to cross before we found our way."
    ~ Carl Sagan'''
    page.println(quote,color=160,center=True)
    filepath = folderPages + pagename + config.extension
    page.save(filepath)

    
#     # dedication
#     pagename = "Dedication"
#     page = libimg.Page()
#     page.vtab(5)
#     page.htab(1)
#     quote = """Dedicated to the Voyager team,
# and to all future explorers..."""
#     page.println(quote,color=160,center=True)
#     filepath = folderPages + pagename + config.extension
#     page.save(filepath)


if __name__ == '__main__':
    os.chdir('..')
    vgPages()
    print 'done'
