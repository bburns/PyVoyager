
"""
vg titles command
build title pages for different targets
called by vg clips command
"""

#. need to build titles for planets/systems and all.mp4 also


import os
import csv

import config
import lib



def vgTitles(targetPath=None):
    "Make titles for specified targetpaths"

    # what does the user want to focus on?
    pathparts = lib.parseTargetPath(targetPath)
    pathSystem, pathCraft, pathTarget, pathCamera = pathparts

    print 'Making titles for', pathparts

    targetpathsSeen = {}

    # iterate through all available images
    reader, f = lib.openCsvReader(config.filesdb)
    for row in reader:
        volume = row[config.filesColVolume]
        fileId = row[config.filesColFileId]
        filter = row[config.filesColFilter]

        system = row[config.filesColPhase]
        craft = row[config.filesColCraft]
        target = row[config.filesColTarget]
        camera = row[config.filesColInstrument]

        # is this an image the user wants to see?
        do = True
        if (pathSystem and pathSystem!=system): do = False
        if (pathCraft and pathCraft!=craft): do = False
        if (pathTarget and pathTarget!=target): do = False
        if (pathCamera and pathCamera!=camera): do = False
        if do:

            # get current file number in that folder, or start at 0
            planetCraftTargetCamera = system + craft + target + camera
            seen = targetpathsSeen.get(planetCraftTargetCamera)
            if not seen:

                # get subfolder and make sure it exists
                # eg data/step8_movies/Jupiter/Voyager1/Io/Narrow/
                subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
                targetfolder = config.titlesFolder + subfolder
                lib.mkdir_p(targetfolder)

                print subfolder + '                  \r',

                # make title image
                # title = target + " Flyby" # eg Triton Flyby
                title = target # eg Triton
                subtitle1 = camera + "-Angle Camera" # eg Narrow-Angle Camera
                subtitle2 = system + " System" # eg Neptune System
                subtitle3 = "Voyager " + craft[-1:] # eg Voyager 2
                img = lib.makeTitlePage(title, subtitle1, subtitle2, subtitle3)

                # save it
                # note: file type must match that of other frames in movie,
                # so use config.extension here
                titlefilepath = targetfolder + 'title' + config.extension
                img.save(titlefilepath)

                # remember this targetpath
                targetpathsSeen[planetCraftTargetCamera] = True

    f.close()
    print



if __name__ == '__main__':
    os.chdir('..')
    vgTitles('//Triton')
    print 'done'
