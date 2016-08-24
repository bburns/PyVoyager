
"""
vg pages command

Build pages like intro, epilogue, credits
"""

import os
import csv

import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import config
import lib
import libimg


class Page:
    "wrapper around PIL text writing routines"
    def __init__(self, sz=800):
        "create a page to write on"
        self.sz = sz
        self.imgsize = [sz,sz] #.param - will be 1000x1000
        self.bgcolor = (0,0,0)
        self.img = Image.new("RGBA", self.imgsize, self.bgcolor)
        self.draw = ImageDraw.Draw(self.img)
        self.pos = [0,0]
        self.size(config.titleFontsize)
        
    def htab(self, col):
        "horizontal tab"
        self.pos[0] = col * self.charWidth
        
    def vtab(self, row):
        "vertical tab"
        self.pos[1] = row * self.charHeight
        
    def size(self, fontsize):
        "change font size"
        self.font = ImageFont.truetype(config.titleFont, fontsize)
        self.charWidth, self.charHeight = self.font.getsize("M")
        self.charHeight *= 1.3 # fudge factor
        
    # def println(self, s, color=200, center=False):
    def println(self, s, color=128, center=False):
        "print a line or sequence of lines"
        lines = s.split('\n')
        fg = (color,color,color)
        for line in lines:
            w,h = self.font.getsize(line)
            if center:
                self.pos[0] = (self.sz - w) / 2
            self.draw.text(self.pos, line, fg, font=self.font)
            # self.pos[1] = self.pos[1] + h*1.25
            self.pos[1] = self.pos[1] + self.charHeight
        
    def save(self, filepath):
        "save page to a file"
        self.img.save(filepath)
        

def vgPages():
    "Make special pages"
    
    # note: ffmpeg requires file type to match that of other frames in movie,
    # so use config.extension.

    folderPages = config.folders['pages']
    
    # intro
    title = "Voyager: The Grand Tour"
    page = Page()
    page.vtab(5)
    page.println(title, color=200, center=True)
    filepath = folderPages + 'Intro' + config.extension
    page.save(filepath)

    # credits
    page = Page()
    page.vtab(5)
    page.htab(1)
    page.println("Credits",color=255)
    page.size(32)
    credits = """Images - NASA/JPL
Music - J.S.Bach
Image processing - Brian Burns
img2png, flatfields - Bjorn Jonsson
Software - Python, OpenCV, SciPy, NumPy, SpiceyPy
With thanks to Mark Showalter, seti.org, NAIF,
planetary.org, UnmannedSpacecraft.com.
"""
    page.println(credits)
    filepath = folderPages + 'Credits' + config.extension
    page.save(filepath)
    
    # epilogue
    page = Page()
    page.vtab(5)
    page.htab(1)
    # quote = """Dedicated to all future explorers..."""
    quote = """Dedicated to the Voyager team,
and all future explorers..."""
    page.println(quote,color=200,center=True)
    filepath = folderPages + 'Epilogue' + config.extension
    page.save(filepath)


if __name__ == '__main__':
    os.chdir('..')
    vgPages()
    print 'done'
