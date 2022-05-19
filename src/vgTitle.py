"""
vg title command

Build title pages for different targets.
Called by the vg clips command.
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



def makeTitlePage(title, subtitle1='', subtitle2='', subtitle3='', center=False):
    """
    Draw a title page, return a PIL image
    """

    font = ImageFont.truetype(config.titleFont, config.titleFontsize)

    imgsize = [config.imsize,config.imsize]
    bgcolor = (0,0,0)
    fgcolor = (200,200,200)

    img = Image.new("RGBA", imgsize, bgcolor)
    draw = ImageDraw.Draw(img)

    top = config.imsize / 2 - 100

    pos = [200,top]
    s = title
    w,h = font.getsize(s)
    if center: pos[0] = config.imsize/2 - w/2
    draw.text(pos, s, fgcolor, font=font)

    fgcolor = (120,120,120)

    pos = [pos[0],pos[1]+h*1.6]
    s = subtitle1
    w,h = font.getsize(s)
    if center: pos[0] = config.imsize/2 - w/2
    draw.text(pos, s, fgcolor, font=font)

    pos = [pos[0],pos[1]+h*1.1]
    s = subtitle2
    w,h = font.getsize(s)
    if center: pos[0] = config.imsize/2 - w/2
    draw.text(pos, s, fgcolor, font=font)

    pos = [pos[0],pos[1]+h*1.1]
    s = subtitle3
    w,h = font.getsize(s)
    if center: pos[0] = config.imsize/2 - w/2
    draw.text(pos, s, fgcolor, font=font)

    return img


def vgTitle(targetPath=None):

    "Make titles for specified targetpaths"

    # what does the user want to focus on?
    targetPathParts = lib.parseTargetPath(targetPath)
    pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    print 'Making titles for', targetPathParts

    targetPathSeen = {}
    systemPathSeen = {}

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.dbFiles)
    for row in csvFiles:

        volume = row[config.colFilesVolume]
        fileId = row[config.colFilesFileId]
        filter = row[config.colFilesFilter]
        system = row[config.colFilesSystem]
        craft = row[config.colFilesCraft]
        target = row[config.colFilesTarget]
        camera = row[config.colFilesCamera]

        # is this an image the user wants to see?
        doTarget = lib.targetMatches(targetPathParts, system, craft, target, camera)
        if target in config.targetsIgnore: doTarget = False

        if doTarget:

            # make sure we haven't seen this target before
            targetKey = system + craft + target + camera # eg JupiterVoyager1IoNarrow
            targetSeen = targetPathSeen.get(targetKey)
            if not targetSeen:

                # get subfolder and make sure it exists
                # eg data/step8_movies/Jupiter/Voyager1/Io/Narrow/
                subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                targetfolder = config.folders['titles'] + subfolder
                lib.mkdir_p(targetfolder)

                print subfolder + '                                         \r',

                # make title image
                title = target # eg Triton
                subtitle1 = camera + "-Angle Camera" # eg Narrow-Angle Camera
                subtitle2 = system + " System" # eg Neptune System
                subtitle3 = "Voyager " + craft[-1:] # eg Voyager 2
                img = makeTitlePage(title, subtitle1, subtitle2, subtitle3)

                # save it
                # note: ffmpeg requires file type to match that of other frames in movie,
                # so use config.extension here
                titlefilepath = targetfolder + 'title' + config.extension
                img.save(titlefilepath)

                # remember this targetpath
                targetPathSeen[targetKey] = True


            # make sure we haven't seen this system before
            systemKey = system + craft # eg JupiterVoyager1
            systemSeen = systemPathSeen.get(systemKey)
            if not systemSeen:

                # get subfolder and make sure it exists
                # eg data/step8_movies/Jupiter/Voyager1/Io/Narrow/
                subfolder = system + '/' + craft + '/'
                systemfolder = config.folders['titles'] + subfolder
                lib.mkdir_p(systemfolder)

                print subfolder + '                                         \r',

                # make title image
                title = system
                subtitle1 = "Voyager " + craft[-1:] # eg Voyager 2
                subtitle2 = ''
                subtitle3 = ''
                img = makeTitlePage(title, subtitle1, subtitle2, subtitle3, center=True)

                # save it
                # note: ffmpeg requires file type to match that of other frames in movie,
                # so use config.extension here
                titlefilepath = systemfolder + 'title' + config.extension
                img.save(titlefilepath)

                # remember this systempath
                systemPathSeen[systemKey] = True


    fFiles.close()
    print


    # # make main title pages
    # title = "Voyager: The Grand Tour"
    # subtitle1 = ''
    # subtitle2 = ''
    # subtitle3 = ''
    # # img = libimg.makeTitlePage(title, subtitle1, subtitle2, subtitle3, center=True)
    # img = makeTitlePage(title, subtitle1, subtitle2, subtitle3, center=True)

    # # save it
    # # note: ffmpeg requires file type to match that of other frames in movie,
    # # so use config.extension here
    # folder = config.folders['titles']
    # titlefilepath = folder + 'title' + config.extension
    # img.save(titlefilepath)

    # # make epilogue
    # title = "Voyager"
    # subtitle1 = ""
    # subtitle2 = 'This is an open source movie - you can help!'
    # subtitle3 = 'See grandtourmovie.org'
    # # img = libimg.makeTitlePage(title, subtitle1, subtitle2, subtitle3, center=True)
    # img = makeTitlePage(title, subtitle1, subtitle2, subtitle3, center=True)

    # # save it
    # # note: ffmpeg requires file type to match that of other frames in movie,
    # # so use config.extension here
    # folder = config.folders['titles']
    # titlefilepath = folder + 'epilogue' + config.extension
    # img.save(titlefilepath)
    


if __name__ == '__main__':
    os.chdir('..')
    vgTitle('//Triton')
    print 'done'
