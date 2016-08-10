
"""
vg titles command

Build title pages for different targets.
Called by the vg clips command.
"""

#. need to build titles for planets/systems and all.mp4 also


import os
import csv

import config
import lib
import libimg



def vgTitles(targetPath=None):
    "Make titles for specified targetpaths"

    # what does the user want to focus on?
    targetPathParts = lib.parseTargetPath(targetPath)
    pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    print 'Making titles for', targetPathParts

    targetPathSeen = {}

    # iterate through all available images
    csvFiles, fFiles = lib.openCsvReader(config.filesdb)
    for row in csvFiles:
        volume = row[config.filesColVolume]
        fileId = row[config.filesColFileId]
        filter = row[config.filesColFilter]

        system = row[config.filesColPhase]
        craft = row[config.filesColCraft]
        target = row[config.filesColTarget]
        camera = row[config.filesColInstrument]

        # is this an image the user wants to see?
        # doTarget = True
        # if (pathSystem and pathSystem!=system): doTarget = False
        # if (pathCraft and pathCraft!=craft): doTarget = False
        # if (pathTarget and pathTarget!=target): doTarget = False
        # if (pathCamera and pathCamera!=camera): doTarget = False
        doTarget = lib.targetMatches(targetPathParts, system, craft, target, camera)

        if doTarget:

            # get current file number in that folder, or start at 0
            planetCraftTargetCamera = system + craft + target + camera
            targetSeen = targetPathSeen.get(planetCraftTargetCamera)
            if not targetSeen:

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
                img = libimg.makeTitlePage(title, subtitle1, subtitle2, subtitle3)

                # save it
                # note: file type must match that of other frames in movie,
                # so use config.extension here
                titlefilepath = targetfolder + 'title' + config.extension
                img.save(titlefilepath)

                # remember this targetpath
                targetPathSeen[planetCraftTargetCamera] = True

    fFiles.close()
    print



if __name__ == '__main__':
    os.chdir('..')
    vgTitles('//Triton')
    print 'done'
