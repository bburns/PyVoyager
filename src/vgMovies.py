
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

# import vgComposite
# import vgAnnotate
# import vgTitle

import vgClips



# won't need concatenate fns until building complete movie

# def concatenateSegments():
#     ""
#     csvMovies, fMovies = lib.openCsvReader(config.dbMovies)
#     lastMovieId = ''
#     segments = []
#     # gather segments for each movieId into array, then call buildSegment
#     for row in csvMovies:
#         movieId = row[0] # eg Neptune-Voyager2
#         targetKey = row[1] # eg Neptune-Voyager2-Triton-Narrow
#         imageIds = row[2] if len(row)>2 else None # eg C1550829-C1618136
#         if movieId != lastMovieId and lastMovieId != '':
#             buildSegment(lastMovieId, segments)
#             segments = []
#         segments.append([targetKey,imageIds])
#         lastMovieId = movieId
#     buildSegment(lastMovieId, segments)
#     fMovies.close()


# # def concatenateClips(movieId, clipIds):
# def concatenateSegment(movieId, segment):
#     "Concatenate the given mp4 clips into an mp4 movie"

#     print 'Generating movie', movieId
#     print movieId, clipIds
#     movieFilepath = config.folders['movies'] + movieId + '.mp4'
#     movieContentsFilepath = config.folders['movies'] + movieId + '.txt'
#     if clipIds != []:
#         makeContentsFile(movieContentsFilepath, clipIds)
#         # now make the movie
#         # eg "ffmpeg -y -f concat -i Neptune-Voyager2.txt -c copy Neptune-Voyager2.mp4"
#         cmd = "ffmpeg -y -f concat -i %s -c copy %s" % (movieContentsFilepath, movieFilepath)
#         print cmd
#         os.system(cmd)




#. from lib
# def makeVideosFromStagedFiles(stageFolder, outputFolder, filespec, frameRate, minFrames):
#     """
#     Build mp4 videos using ffmpeg on sequentially numbered image files.
#     stageFolder contains the sequentially number files, eg data/step10_clips/stage/.
#     outputFolder is where the mp4 clips will go.
#     filespec describes the filenames, eg 'foo%04d.png'.
#     frameRate is in fps
#     minFrames is the minimum number of frames needed to build a video.
#     """
#     print 'Making mp4 clips using ffmpeg'
#     for root, dirs, files in os.walk(stageFolder):
#         # print root, dirs
#         if dirs==[]: # reached the leaf level
#             nfiles = len(files)
#             if nfiles >= minFrames:
#                 # root = eg data/step10_clips/stage/Neptune\Voyager2\Triton\Narrow\Bw
#                 print 'Directory', root
#                 stageFolderPath = os.path.abspath(root)
#                 # get target file path relative to staging folder,
#                 # eg ../../Neptune-Voyager-Triton-Narrow-Bw.mp4
#                 targetFolder = root[len(stageFolder):] # eg Neptune\Voyager2\Triton\Narrow\Bw
#                 targetPath = targetFolder.split('\\') # eg ['Neptune','Voyager2',...]
                # # videoFiletitle eg 'Neptune-Voyager2-Triton-Narrow-Bw.mp4'
                # videoFiletitle = '-'.join(targetPath) + '.mp4'
                # # videoFilepath = '../../../../../../' + videoFiletitle
                # imagesToMp4(stageFolderPath, filespec, videoFilepath, frameRate)

# def buildTargetMovie(targetKey, subtargets):
#     """
#     build an mp4 movie from the given subtargets.
#     targetKey will be the name of the movie (with .mp4 appended).
#     subtargets is an array of [targetKey, imageIds].
#     """
#     print targetKey
#     # "build the movie targetKey.mp4 from the given subtarget movies or image segments"
#     movieFolder = lib.getFolder('movies') # eg data/movies
#     movieFilepath = movieFolder + targetKey + '.mp4' # eg data/movies/Jupiter-Voyager1.mp4
#     for row in subtargets:
#         #. add subtarget movie to file list
#         buildSubtargetMovies(targetKey, subtargets)
#         #. concatenate subtarget movies to target movie
#         # targetPath = targetKey.replace('-','/')
#         # targetPathParts = lib.parseTargetPath(targetPath)
#         # print targetKey, imageIds
            
                
def buildSegment(segmentId, subsegments):
    """
    build an mp4 movie segment from its mp4 subsegments
    eg in movies.csv,
    segmentId, subsegmentId, contents
    Jupiter-Voyager1-Ganymede, Jupiter-Voyager1-Ganymede-Narrow, C1460413-C1640725
    Jupiter-Voyager1-Ganymede, Jupiter-Voyager1-Ganymede-Wide, C1640141-C1640752
    builds
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
            subsegmentPath = subsegmentId.replace('-','/')
            subsegmentPath = subsegmentId.replace('@','/') # eg jupiter/voyager1/jupiter/clouds
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
        print 'add subsegmentmovie to filelist', subsegmentFilepath
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
    
    for segment in segments:
        key = segment[0]
        rows = segment[1]
        buildSegment(key, rows)
    

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


