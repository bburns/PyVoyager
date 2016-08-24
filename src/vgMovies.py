
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
    stageFolder = config.moviesStageFolder
    subsegmentFilepaths = []
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
        subsegmentFilepath = movieFolder + subsegmentFiletitle + qualifier + '.mp4' 
        subsegmentFilepath = os.path.abspath(subsegmentFilepath)
        
        # build subsegment movie if doesn't already exist
        if not os.path.isfile(subsegmentFilepath):
            subsegmentPath = subsegmentId
            subsegmentPath = subsegmentPath.replace('-','/')
            subsegmentPath = subsegmentPath.replace('@','/') # eg jupiter/voyager1/jupiter/clouds
            subsegmentStageFolder = stageFolder + subsegmentPath
            
            # make stage folder
            print 'rmdir+mkdir',subsegmentStageFolder
            lib.rmdir(subsegmentStageFolder)
            lib.mkdir_p(subsegmentStageFolder)
            
            # stage images for ffmpeg
            print 'stagefiles', subsegmentPath, contents, stageFolder
            # can't pass a full array of imageids as there could be an interval of 200k,
            # so pass string range in 'contents'
            vgClips.stageFiles(None, subsegmentPath, contents, stageFolder)

            # build mp4 files from all staged images
            # subsegmentFilepathRelative = '../../../' + subsegmentFilepath
            print 'makevideo with imagesToMp4 ->',subsegmentFilepath
            # lib.imagesToMp4(subsegmentStageFolder, config.videoFilespec,
                            # subsegmentFilepath, config.videoFrameRate)
            lib.imagesToMp4(subsegmentStageFolder, subsegmentFilepath)
            
        # add subsegment movie to filelist
        print 'add subsegment to filelist', subsegmentFilepath
        subsegmentFilepaths.append(subsegmentFilepath)
        
    # compile subsegment movies into single movie
    segmentFilepath = movieFolder + segmentId + '.mp4'
    print 'all subsegment movies created. now compile into single movie',segmentFilepath
    print subsegmentFilepaths
    lib.concatenateMovies(segmentFilepath, subsegmentFilepaths)
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
        segmentId = segment[0]
        subsegments = segment[1]
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


