
# vg segments command
# build segments, which can combine narrow/wide angle, bw/color,
# have variable frame rates, and annotations.
# uses db/segments.csv
# eg vg segments Jupiter/Voyager1/Io builds Jupiter-Voyager1-Io.mp4

# this must be run in an admin console because mklink requires elevated privileges


import csv
import os
import os.path

import config
import lib

# import vgBuildTitles

# includeTitles = True
# includeTitles = False




def stageFiles(targetPathParts):
    "Make links from source files to segment stage folders"

    print 'Making links from source files'

    # what does the user want to focus on?
    pathSystem, pathCraft, pathTarget, pathCamera = targetPathParts

    # read some small dbs into memory
    # targetInfo = lib.readCsv(config.targetsdb) # remapping listed targets
    # framerateInfo = lib.readCsv(config.frameratesdb) # change framerates
    # centeringInfo = lib.readCsv(config.centeringdb) # turn centering on/off
    # segmentInfo = lib.readCsv(config.segmentsdb)

    # keep track of number of files in each target subfolder,
    # so we can number files appropriately and know when to add titles
    nfilesInTargetDir = {}

    # how many times should we duplicate the images?
    ncopiesPerImage = 1 # default
    ncopiesPerImageMemory = {} # keyed on planet-spacecraft-target

    # iterate through all available images
    f = open(config.segmentsdb, 'rt')
    i = 0
    lastSegmentId=''
    reader = csv.reader(f)
    for row in reader:
        if row==[] or row[0][0]=="#": continue # ignore blank lines and comments
        if i==0: fields = row
        else:
            # read file info
            segmentId = row[config.segmentsColSegmentId]
            imageIds = row[config.segmentsColImageIds]
            imageSource = row[config.segmentsColImageSource]
            nframes = row[config.segmentsColNFrames]
            # if len(row)>=config.segmentsColAnnotation:
                # annotation = row[config.segmentsColAnnotation]

            # show progress
            if segmentId!=lastSegmentId:
                print 'SegmentId %s    \r' % segmentId,
                lastSegmentId = segmentId

            # how do we get the image?
            # we have the imageId range - loop over that,




            # # system = row[config.filesColPhase]
            # # craft = row[config.filesColCraft]
            # # target = row[config.filesColTarget]
            # # camera = row[config.filesColInstrument]

            # # # relabel target field if necessary - see db/targets.csv for more info
            # # targetInfoRecord = targetInfo.get(fileId)
            # # if targetInfoRecord:
            # #     # make sure old target matches what we have
            # #     if targetInfoRecord['oldTarget']==target:
            # #         target = targetInfoRecord['newTarget']

            # # does this image match the target path the user specified on the cmdline?
            # addImage = True
            # if (pathSystem and pathSystem!=system): addImage = False
            # if (pathCraft and pathCraft!=craft): addImage = False
            # if (pathTarget and pathTarget!=target): addImage = False
            # if (pathCamera and pathCamera!=camera): addImage = False
            # if addImage:

            #     # build a key
            #     planetCraftTargetCamera = system + '-' + craft + '-' + target + '-' + camera

            #     # # how many copies of this file should we stage?
            #     # framerateInfoRecord = framerateInfo.get(fileId) # record from framerates.csv
            #     # if framerateInfoRecord:
            #     #     # eg ncopies = 3 = 3x slowdown
            #     #     ncopiesPerImage = int(framerateInfoRecord['nframesPerImage'])
            #     #     # remember it for future also
            #     #     # eg key Uranus-Voyager2-Arial-Narrow
            #     #     key = framerateInfoRecord['planetCraftTargetCamera']
            #     #     ncopiesPerImageMemory[key] = ncopiesPerImage
            #     # else:
            #     #     # lookup where we left off for this target, or 1x speed if not seen before
            #     #     ncopiesPerImage = ncopiesPerImageMemory.get(planetCraftTargetCamera) or 1

            #     # # get image source path
            #     # # eg data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
            #     # #. make this a fn - duplicated elsewhere
            #     # centeringInfoRecord = centeringInfo.get(planetCraftTargetCamera)
            #     # if centeringInfoRecord:
            #     #     centeringOff = centeringInfoRecord['centeringOff']
            #     #     centeringOn = centeringInfoRecord['centeringOn']
            #     #     docenter = fileId<centeringOff or fileId>centeringOn
            #     # else: # if no info for this target just center it
            #     #     docenter = True

            #     # if centering for this image is turned off, let's assume for now that
            #     # that means we don't want the color image, since it'd be misaligned anyway.
            #     if docenter==False:
            #         pngSubfolder = config.adjustmentsFolder + 'VGISS_' + volume + '/'
            #         pngfilename = config.adjustmentsPrefix + fileId + '_' + \
            #                       config.imageType + '_' + filter + '.png'
            #     elif bwOrColor=='bw':
            #         pngSubfolder = config.centersFolder + 'VGISS_' + volume + '/'
            #         pngfilename = config.centersPrefix + fileId + '_' + \
            #                       config.imageType + '_' + filter + '.png'
            #     else:
            #         pngSubfolder = config.compositesFolder + 'VGISS_' + volume + '/'
            #         pngfilename = config.compositesPrefix + fileId + '.png'
            #     pngpath = pngSubfolder + pngfilename

            #     # if image file exists, create subfolder and link image
            #     if os.path.isfile(pngpath):

            #         # get staging subfolder and make sure it exists
            #         # eg data/step09_clips/stage/Jupiter/Voyager1/Io/Narrow/Bw/
            #         subfolder = system + '/' + craft + '/' + target + '/' + camera + '/'
            #         subfolderPlusColor = subfolder + bwOrColor.title() + '/'
            #         targetfolder = config.clipsStageFolder + subfolderPlusColor
            #         lib.mkdir_p(targetfolder)

            #         # get current file number in that folder, or start at 0
            #         nfile = nfilesInTargetDir.get(planetCraftTargetCamera)
            #         if not nfile: nfile = 0

            #         # if we haven't seen this subfolder before, add the titlepage image a few times.
            #         # titlepages are created in the previous step, vgBuildTitles.
            #         if includeTitles and nfile==0:
            #             titleimagefilepath = config.titlesFolder + subfolder + 'title.png'
            #             # need to get out of the target dir - we're always this deep
            #             titleimagepathrelative = '../../../../../../../../' + titleimagefilepath
            #             ntitlecopies = config.clipFramesForTitles
            #             lib.makeSymbolicLinks(targetfolder, titleimagepathrelative,
            #                                   nfile, ntitlecopies)
            #             nfile += ntitlecopies

            #         # link to file
            #         # note: mklink requires admin privileges,
            #         # so must run this script in an admin console
            #         # eg pngpath=data/step3_centers/VGISS_5101/centered_C1327321_RAW_Orange.png
            #         # need to get out of the target dir
            #         pngpathrelative = '../../../../../../../../' + pngpath
            #         lib.makeSymbolicLinks(targetfolder, pngpathrelative, nfile, ncopiesPerImage)
            #         print nfile, pngpathrelative

            #         # increment the file number for the target folder
            #         nfile += ncopiesPerImage
            #         nfilesInTargetDir[planetCraftTargetCamera] = nfile

        i += 1

    f.close()
    print


def vgSegments(targetPath=''):
    "Build segments associated with the given target path (eg //Io)"

    # note: targetPathParts = [pathSystem, pathCraft, pathTarget, pathCamera]
    # but we can ignore the camera part
    targetPathParts = lib.parseTargetPath(targetPath)

    # make sure we have some titles
    # vgBuildTitles.buildTitles(targetPath)

    # stage images for ffmpeg
    lib.rmdir(config.segmentsStageFolder)
    stageFiles(targetPathParts)

    # build mp4 files from all staged images
    # lib.makeVideosFromStagedFiles(config.segmentsStageFolder, '../../../../../',
                                  # config.videoFilespec, config.videoFrameRate)


if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # vgSegments('bw', 'Jupiter/Voyager1/Io/Narrow')
    # vgSegments('bw', '//Triton')
    # vgSegments("Neptune")
    vgSegments()
    # makeLinks()
    # makeSegmentFiles()
    print 'done'


