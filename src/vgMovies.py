"""
vg movies command

Combine segments into complete movies, eg
> vg movies Jupiter/Voyager1

This must be run in an admin console because mklink requires elevated privileges.
"""

import csv
import os
import os.path

import config
import lib

import vgClips


def buildSegment(segmentId, subsegments):
    """
    build an mp4 movie segment from its subsegments, building them if necessary.
    eg if segmentId='Jupiter-Voyager1-Ganymede', and
    subsegments=
    [['Jupiter-Voyager1-Ganymede', 'Jupiter-Voyager1-Ganymede-Narrow', 'C1460413-C1640725'],
     ['Jupiter-Voyager1-Ganymede', 'Jupiter-Voyager1-Ganymede-Wide', 'C1640141-C1640752']]
    then this would build
    Jupiter-Voyager1-Ganymede.mp4 
    from
    Jupiter-Voyager1-Ganymede-Narrow-C1460413-C1640725.mp4
    Jupiter-Voyager1-Ganymede-Wide-C1640141-C1640752.mp4
    building the latter if they don't already exist.
    """
    print 'buildsegment',segmentId
    movieFolder = config.folders['movies']
    pagesFolder = config.folders['pages']
    stageFolder = config.moviesStageFolder
    filepaths = []
    for subsegment in subsegments:
        print subsegment
        subsegmentId = subsegment[1].strip() # eg Neptune-Voyager2-Triton-Narrow
        contents = subsegment[2].strip() if len(subsegment)>2 else None # eg C1550829-C1618136
        
        #.remove partname from segmentid
        # a = subsegmentId.split('@')
        # if len(a)>1:
            # partname = a[1]
            # print 'got partname',partname
            
        # get name of subsegment movie file
        subsegmentFiletitle = subsegmentId # eg 'Jupiter-Voyager1-Jupiter@Clouds'
        qualifier = '-' + contents if contents else '' # eg '-C1550829-C1618136'
        filepath = movieFolder + subsegmentFiletitle + qualifier + '.mp4' 
        filepath = os.path.abspath(filepath)

        # build subsegment movie if doesn't already exist
        if not os.path.isfile(filepath):
            
            subsegmentPath = subsegmentId
            subsegmentPath = subsegmentPath.replace('-','/')
            subsegmentPath = subsegmentPath.replace('@','/') # eg jupiter/voyager1/jupiter/clouds
            subsegmentStageFolder = stageFolder + subsegmentPath + '/'

            # make stage folder
            print 'rmdir+mkdir',subsegmentStageFolder
            lib.rmdir(subsegmentStageFolder)
            lib.mkdir_p(subsegmentStageFolder)

            #. handle special subsegmentIds - Intro, Credits, Epilogue
            if subsegmentId in ['Intro', 'Prologue', 'Credits', 'Epilogue']:
                
                #. make a movie of credit jpg and add to filepaths
                pageFilepath = pagesFolder + subsegmentId + config.extension
                # pageFilepath = os.path.abspath(pageFilepath)
                # add links to file
                # targetFolder = stageFolder + subsegmentId + '/'
                # lib.rmdir(subsegmentStageFolder)
                # lib.mkdir_p(subsegmentStageFolder)
                # lib.addImages(pageFilepath, targetFolder, ncopies)
                # sourcePath = '../../../' + pageFilepath
                sourcePath = '../../../../' + pageFilepath
                ncopies = 50 #. param
                lib.makeSymbolicLinks(sourcePath, subsegmentStageFolder, ncopies)
                
                # build mp4 files from all staged images
                print 'makevideo with imagesToMp4 ->',filepath
                lib.imagesToMp4(subsegmentStageFolder, filepath)
            else:        
                # stage images for ffmpeg
                print 'stagefiles', subsegmentPath, contents, stageFolder
                vgClips.stageFiles(None, subsegmentPath, contents, stageFolder)

                # build mp4 files from all staged images
                print 'makevideo with imagesToMp4 ->',filepath
                lib.imagesToMp4(subsegmentStageFolder, filepath)
            
        # add movie to filelist so can concatenate them later
        print 'add subsegment to filelist', filepath
        filepaths.append(filepath)
        
    # compile subsegment movies into single movie
    segmentFilepath = movieFolder + segmentId + '.mp4'
    print 'all subsegment movies created. now compile into single movie',segmentFilepath
    print filepaths
    lib.concatenateMovies(segmentFilepath, filepaths)
    
    # now remove intermediaries below a certain level, eg don't really want
    # Jupiter-Voyager1-Europa-Narrow hanging around.
    # but if they're gone they'll have to be rebuilt each time...
    # print 'cleanup'
    # if len(segmentId.split('-'))>=4:
        # for filepath in filepaths:
            # lib.rm(filepath)
    print


def vgMovies(filterVolumes=None, filterTargetPath=None, keepLinks=False):
    """
    Build movies associated with the given volumes AND target path (eg '//Io').
    """
    # walk over movies.csv and build each segment listed there that matches given filters
    
    # get array of segments to add
    segments = lib.readCsvGroups(config.dbMovies)
    
    # build each segment
    for segment in segments:
        segmentId = segment[0] # eg 'Jupiter-Voyager1-Ganymede'
        subsegments = segment[1] # array of associated rows from movies.csv
        buildSegment(segmentId, subsegments)
    

if __name__ == '__main__':
    os.chdir('..')
    # print lib.parseTargetPath('')
    # vgMovies('Jupiter/Voyager1/Io/Narrow')
    # vgMovies('//Triton')
    # vgMovies("Neptune")
    vgMovies("Jupiter")
    # makeLinks()
    # makeClipFiles()
    print 'done'


