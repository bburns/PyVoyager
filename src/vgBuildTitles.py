
# build title pages for different targets

import os
import csv

import config
import lib



def buildTitles(targetPath=None):
    "make titles for specified targetpaths"

    # what does the user want to focus on?
    pathparts = lib.parseTargetPath(targetPath)
    pathSystem, pathCraft, pathTarget, pathCamera = pathparts

    print 'making titles for', pathparts

    targetpathsSeen = {}

    # iterate through all available images
    f = open(config.filesdb, 'rt')
    i = 0
    reader = csv.reader(f)
    for row in reader:
        if row==[] or row[0][0]=="#": continue # ignore blanks and comments
        elif i==0: fields = row
        else:
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
                    subfolder = system +'/' + craft + '/' + target +'/' + camera + '/'
                    targetfolder = config.titlesFolder + subfolder
                    lib.mkdir_p(targetfolder)

                    print subfolder + '                  \r',

                    # make title image
                    title = target + " Flyby" # eg Triton Flyby
                    subtitle1 = camera + "-Angle Camera" # eg Narrow-Angle Camera
                    subtitle2 = system + " System" # eg Neptune System
                    subtitle3 = "Voyager " + craft[-1:] # eg Voyager 2
                    img = lib.makeTitlePage(title, subtitle1, subtitle2, subtitle3)

                    # save it
                    titlefilepath = targetfolder + 'title.png'
                    img.save(titlefilepath)

                    # remember this targetpath
                    targetpathsSeen[planetCraftTargetCamera] = True

        i += 1

    f.close()



if __name__ == '__main__':

    os.chdir('..')

    buildTitles('//Triton')

    # import os
    # os.system(filename)

    print 'done'
