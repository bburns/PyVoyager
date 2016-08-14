
# Voyager config options
#--------------------------------------------------------------------------------




# Global settings
# ----------------------------------------

# include titles in clips?
# includeTitles = True
includeTitles = False

# use jpegs for faster development time, less space
useJpegs = True
# useJpegs = False
extension = '.jpg' if useJpegs else '.png'

logfile = 'log.txt'



# Voyager
# ----------------------------------------

# camera field of views, in degrees
# source: http://pds-rings.seti.org/voyager/iss/inst_cat_na1.html
cameraFOVs = {'Narrow': 0.424, 'Wide': 3.169}


# Download
# ----------------------------------------

# voyager archive url
downloadUrl = "http://pds-rings.seti.org/archives/VGISS_{}xxx/VGISS_{}.tar.gz"


# Convert
# ----------------------------------------

# imagetype for main processing
# RAW images can have overly bright backgrounds.
# CLEANED images have the riseau marks removed, but not very well.
# CALIB images have darker backgrounds, but can dim the planet too much.
# GEOMED images are corrected for geometric distortions also, but are upped to 1000x1000.
# imageType = 'RAW'
imageType = 'CALIB'
# imageFilespec = "*" + imageType + ".IMG" # eg *CALIB.IMG
# imageFilespec = "*" # do all image types

# image types to extract using img2png
# imageTypes = ['RAW', 'CLEANED', 'CALIB', 'GEOMED']
# imageTypes = ['RAW', 'CLEANED', 'CALIB']
# imageTypes = ['CLEANED', 'CALIB']
# imageTypes = ['CLEANED']
# imageTypes = ['RAW']
# imageTypes = ['CALIB']
imageTypes = ['RAW','CALIB']
imageFilespecs = ["*" + imageType + ".IMG" for imageType in imageTypes]

# img2png options
# -fnamefilter - append filter name, eg _ORANGE
# -loglevel<level> - debug info
# -s<level> - scale image values by this amount - otherwise can be too dark
# note: -s10 works for uranus but blows out jupiter images -
# would need per-flyby and lots of experimenting,
# so just keep using the dim CALIB images and histogram stretching, which works well.
# img2pngOptions = "-fnamefilter -loglevel0 -s10"
img2pngOptions = "-fnamefilter -loglevel0"



# Adjust
# ----------------------------------------

# targets over this size (fraction of the image frame)
# won't get histogram stretched (can blow out small targets)
adjustHistogramImageFractionMinimum = 0.25


# Denoise
# ----------------------------------------


# Center
# ----------------------------------------

# this can be a filetitle path for the centering algorithms to save intermediate
# stage images to, eg 'test/images/debug/C1382377' - it will append '_canny.jpg',
# '_binary.jpg', etc and save the files there.
debugImageTitle = None

# if you try changing these values, make sure to run 'vg test'
# to see how they affect the test images

# fraction of image which needs to be taken up by target before centering is turned off
imageFractionCenteringThreshold = 1.2

# don't want to center these targets
dontCenterTargets = 'Dark,Sky,Plaque,Cal_Lamps,Orion,Vega,Star,Pleiades,Scorpius,\
Sigma_Sgr,Beta_Cma,Arcturus,Taurus,Theta_Car,J_Rings,S_Rings,U_Rings,N_Rings'.split(',')

# these targets aren't in the PCK datafile so don't know radius,
# but want to try to center on them - just assume they're tiny
#. if necessary could give them values here
centerTargets = 'Amalthea,Thebe,Adrastea,Metis,Larissa,System,Phoebe,Unk_Sat,Helene,\
Prometheus,Pandora,Calypso,Proteus,Janus,Telesto,Puck,Epimetheus'.split(',')


# blob detection
# --------------------

# level at which to take binary threshold for blob detection
# level is 0.0-1.0 for scipy images
# blobThreshold = 0.15 # worked with the -s10 option with uranus
# blobThreshold = 0.05
# blobThreshold = 0.025
# blobThreshold = 0.012 # works for most, but small triton, which has light corners
# blobThreshold = 0.016 # to v0.35 works for most neptune system images (* 256 0.016) 4.096
# blobThreshold = 0.015 # v0.36 works for most neptune system images (* 256 0.015) 3.84
# blobThreshold = 0.02
# level is 0-255 with cv2 images
# blobThreshold = 2
# blobThreshold = 3
# blobThreshold = 4

# adaptive thresholding
blobAdaptiveThresholdSize = 9 # v0.42
blobAdaptiveThresholdConstant = 6 # v0.42

# area in pixels^2 at which switch from blob detection to hough circle detection.
# mainly depends on the minimum size circle that hough can detect.
# blob detection works best for small sources - hough for bigger circles
# blobAreaCutoff = 10*10 # missed some small but sharp circles
# blobAreaCutoff = 14*14 # missed triton small but clear
# blobAreaCutoff = 20*20
# blobAreaCutoff = 24*24
# blobAreaCutoff = 30*30 # v0.36ish

blobRadiusMax = 10 # v0.42

# circle detection
# --------------------

# hough circle detector parameters

# size of accumulator space relative to image
# would think increasing this would help with jitters,
# but just made tests worse
#. try again, reduce accthresh also
houghAccumulatorSize = 1 # always
# houghAccumulatorSize = 2 # always

houghMinDistanceBetweenCircles = 400

# canny edge detection threshold
# used by hough circle detection - lower threshold is half of this
# if this is too high then dim circles won't be detected
# but if it's too low you'd get too many spurious edges in the edge image
# houghCannyUpperThreshold = 250 # v0.36 and prior
houghCannyUpperThreshold = 200 # v0.37 works on dim neptune with noise AND regular jupiter

# houghAccumulatorThreshold = 1 # v0.37
# houghAccumulatorThreshold = 5 # v0.42
# houghAccumulatorThreshold = 10 # v0.42
houghAccumulatorThreshold = 20 # v0.42 increased to this and did better because more canny searches

houghRadiusSearchPercent = 10


# stabilization
# --------------------

# if radius of target in image is too different from previous frame,
# assume there's an error and don't try to stabilize the image.
# needs to be large enough to be able to track a target from near to far,
# but still filter out large jumps, so a bit tricky
#. should be a percentage?
# stabilizeMaxRadiusDifference = 20 # v0.40 uranus
# stabilizeMaxRadiusDifference = 50 # v0.41 jupiter
# stabilizeMaxRadiusDifference = 800 # v0.42 see if will work with uncentered targets - #.. almost - need to get rough center using blob, the let stabilizer handle the rest

# ECC parameters
#. try reducing these to speed it up - images shouldn't have shifted very much.
# do some tests to determine good values
# stabilizeECCIterations = 10000
# stabilizeECCIterations = 5000 # v0.40 uranus
# stabilizeECCIterations = 4000
# stabilizeECCIterations = 2000
# stabilizeECCIterations = 1000 # v0.41 jupiter
stabilizeECCIterations = 500 # v0.43 uranus

# stabilizeECCTerminationEpsilon = 1e-12
# stabilizeECCTerminationEpsilon = 1e-11
# stabilizeECCTerminationEpsilon = 1e-10 # v0.40 uranus
# stabilizeECCTerminationEpsilon = 1e-9
# stabilizeECCTerminationEpsilon = 1e-8
# stabilizeECCTerminationEpsilon = 1e-6 # v0.41 jupiter
stabilizeECCTerminationEpsilon = 1e-5 # v0.43 uranus

# if image needs to shift too much, assume something is wrong - don't shift it
# stabilizeMaxDeltaPosition = 18 # v0.40 uranus
# stabilizeMaxDeltaPosition = 20
# stabilizeMaxDeltaPosition = 30
# stabilizeMaxDeltaPosition = 40 # v0.41 jupiter
# stabilizeMaxDeltaPosition = 800 # v0.42 let it try to shift uncentered targets also

# how many times to use fixed frame before getting new one
# if this is 1 the target may drift off to the left
# if it's 9999 the target may stutter towards the end of the volume
# stabilizeNTimesFixedFrameUsed = 10 # v0.41 jupiter
# stabilizeNTimesToUseFixedFrame = 10 # v0.41 jupiter
# stabilizeNTimesToUseFixedFrame = 100 # v0.42 try for uranus - still glitchy
# stabilizeNTimesToUseFixedFrame = 400 # v0.42 try for neptune
# stabilizeNTimesToUseFixedFrame = 9999 # v0.42 try for jupiter - ie turn off, with round instead of int - see if fixes leftward drift. oops - trying to align to first frame all the time -> jitters
# stabilizeNTimesToUseFixedFrame = 1 # v0.42 try jupiter - align to previous frame, using round instead of int, try to fix leftward drift


# suffix for centered filenames
# centersSuffix = '_centered'

# rotate image 180 degrees during centering step
rotateImage = True

# debugging image options during centering step
# used by test/testCentering.py - don't use for normal processing!
#. just make one flag
drawBinaryImage = False # save thresholded image
drawBoundingBox = False # save image with bounding box around biggest blob
drawEdges = False # save canny edges image ~ used by hough circle detector
drawCircle = False # save image with best detected hough circle
drawCircles = False # save image with all detected hough circles
drawCrosshairs = False # draw crosshairs on image
drawTarget = False # draw expected target size/location with yellow circle


# Composite
# ----------------------------------------


# Mosaic
# ----------------------------------------


# Annotate
# ----------------------------------------

annotationsFont = "c:/windows/fonts/!futura-light.ttf"
annotationsFontsize = 18


# Target
# ----------------------------------------

targetsIgnore = dontCenterTargets


# Titles
# ----------------------------------------

titleSecondsToShow = 4

titleFont = "c:/windows/fonts/!futura-light.ttf"
titleFontsize = 48


# Videos (clips, segments, movies)
# ----------------------------------------

# filename used for frames
videoFilespec = 'img%05d' + extension

# frame rate - frames per second
# videoFrameRate = 5 # nowork - gets stuck after a bit - why?
# videoFrameRate = 8 # nice for ariel flyby
# videoFrameRate = 10
# videoFrameRate = 12 # good for triton flyby
# videoFrameRate = 15
# videoFrameRate = 20 # up to v0.43
videoFrameRate = 25 # v0.43 needs to be a bit faster, for uranus
# videoFrameRate = 30

# ffmpeg options
# -y forces overwriting existing file
# -c:v specifies
# -crf specifies constant rate factor
#      see https://trac.ffmpeg.org/wiki/Encode/H.264#crf
#      0 is completely lossless, 18 is very lossless, 23 is default, 51 is worst
# Use -pix_fmt yuv420p for compatibility with outdated media players
#   (including Windows Media Player and Quicktime)
# see http://superuser.com/questions/874583/lossless-h-264-mp4-file-created-from-images-cannot-be-played-in-quicktime
videoFfmpegOptions = "-y -loglevel warning"
# videoFfmpegOutputOptions = "-c:v libx264 -pix_fmt yuv420p -crf 23"
# videoFfmpegOutputOptions = "-c:v libx264 -crf 18" # doubles size of mp4 file over crf23
# videoFfmpegOutputOptions = "-c:v libx264 -crf 23"
#. get warning: deprecated pixel format used, make sure you did set range correctly
# how get rid of it?
# videoFfmpegOutputOptions = "-c:v libx264 -pix_fmt yuv420p -crf 23"
videoFfmpegOutputOptions = "-c:v libx264 -pix_fmt yuvj420p -crf 23" #. try this? mjpeg? (note J)
# videoFfmpegOutputOptions = "-c:v libx264 -pix_fmt yuv420p color_range 3 -crf 23" # nowork


# Clips
# ----------------------------------------

# don't want to make clips for these targets
clipsIgnoreTargets = dontCenterTargets

# these targets aren't in the PCK datafile so don't know radius,
# but want to try to center on them - just assume they're tiny
# centerTargets = 'Amalthea,Thebe,Adrastea,Metis,Larissa,System,Phoebe,Unk_Sat,Helene,\
# Prometheus,Pandora,Calypso,Proteus,Janus,Telesto,Puck,Epimetheus'.split(',')

# used to determine nframes per image - this multiplied by imageFraction,
# so slows down when closer to target
# this can be overridden in targets.csv
# clipsDefaultFrameRateConstant = 60
frameRateConstantDefault = 60

# the max number of copies for each frame (higher=slower movie)
# clipsMaxFrameRateConstant = 30 # v0.43 uranus
# clipsMaxFrameRateConstant = 20 # v0.43 jupiter
# frameRateConstantMax = 20 # v0.43 jupiter
frameRateNCopiesMax = 20 # v0.43 jupiter

# minimum number of frames for a clip to be generated
# (otherwise get lots of 0:00 movies)
clipsMinFrames = 20


# Movies
# ----------------------------------------






# Files and folders
# --------------------------------------------------------------------------------

# convention: all folders should end with /

# folders for data and images
# use offline folder for large datasets (multi gigabyte)
onlineFolder  = "data/"
offlineFolder = "data/" # e.g. could be f:/...

folders = {
    'download':   offlineFolder + 'step01_download/',
    'unzip':      offlineFolder + 'step02_unzip/',
    'convert':    onlineFolder  + "step03_convert/",
    'adjust':     onlineFolder  + "step04_adjust/",
    'denoise':    onlineFolder  + "step05_denoise/",
    'center':     onlineFolder  + "step06_center/",
    'inpaint':    onlineFolder  + "step07_inpaint/",
    'composite':  onlineFolder  + "step08_composite/",
    'mosaic':     onlineFolder  + "step09_mosaic/",
    'annotate':   onlineFolder  + "step10_annotate/",
    'target':     onlineFolder  + "step11_target/",
    'titles':     onlineFolder  + "step12_titles/",
    'clips':      onlineFolder  + "step13_clips/",
    'movies':     onlineFolder  + "step14_movies/",
    'additions':  onlineFolder  + "images/",
    }

clipsStageFolder    = folders['clips'] + 'stage/'

# grab folders - see vg grab
grabFolder = onlineFolder  + "grab/"
grabbedFolder = onlineFolder  + "grabbed/"

# test images go here
testFolder = 'test/'
testCenterdb = testFolder + 'testCenterImages.csv'
testCenterImagesFolder = testFolder + 'center/'
testDenoiseImagesFolder = testFolder + 'denoise/'

musicFolder = 'music/'


# parts of filenames
suffixes = {
    'convert':   '',
    'adjust':    '_adjusted',
    'denoise':   '_denoised',
    'center':    '_centered',
    'inpaint':   '_inpainted',
    'composite': '_composite',
    'mosaic':    '_mosaic',
    'annotate':  '_annotated',
    }

# database folder
dbFolder = 'db/'

# csv file databases
dbFiles              = dbFolder + 'files.csv'
dbCentering          = dbFolder + 'centering.csv'
dbCenters            = dbFolder + 'centers.csv'
dbCentersOverride    = dbFolder + 'centersOverride.csv'
dbCentersNew         = dbFolder + 'centersNew.csv'
dbComposites         = dbFolder + 'composites.csv'
dbCompositing        = dbFolder + 'compositing.csv'
dbMosaics            = dbFolder + 'mosaics.csv'
dbMovies             = dbFolder + 'movies.csv'
dbRetargeting        = dbFolder + 'retargeting.csv'
dbFramerates         = dbFolder + 'framerates.csv'
dbFramerateConstants = dbFolder + 'framerateConstants.csv'
dbSegments           = dbFolder + 'segments.csv'
dbPositions          = dbFolder + 'positions.csv'
dbErrata             = dbFolder + 'errata.csv'
dbAdditions          = dbFolder + 'additions.csv'
dbDenoising          = dbFolder + 'denoising.csv'

# index file folder
indexFolder = 'db/index/'

# useful columns in the index files
# (see db/index/readme.md)
# indexfile     = 'data/index/rawimages.tab'
colIndexVolume       = 0 # eg VGISS_5101
colIndexFilename     = 2 # eg C1389407_GEOMED.IMG
colIndexFiletype     = 3 # eg CALIBRATED_IMAGE
colIndexCraft        = 4 # eg VOYAGER 1
colIndexPhase        = 5 # eg JUPITER ENCOUNTER
colIndexTarget       = 6 # eg IO
colIndexTime         = 9 # eg 1979-03-05T15:32:56
colIndexTimeReceived = 10 # eg 1979-03-05T15:32:56
colIndexInstrument   = 11 # eg WIDE ANGLE CAMERA
colIndexFilter       = 16 # eg ORANGE
colIndexNote         = 19 # eg 3 COLOR ROTATION MOVIE

# index field value translations
# see vgInitFiles.py
indexTranslations = {
    'VOYAGER 1': 'Voyager1',
    'VOYAGER 2': 'Voyager2',
    'JUPITER ENCOUNTER': 'Jupiter',
    'SATURN ENCOUNTER': 'Saturn',
    'URANUS ENCOUNTER': 'Uranus',
    'NEPTUNE ENCOUNTER': 'Neptune',
    'WIDE ANGLE CAMERA': 'Wide',
    'NARROW ANGLE CAMERA': 'Narrow',
    'CALIBRATED_IMAGE': 'Calibrated',
    'CLEANED_IMAGE': 'Cleaned',
    'DECOMPRESSED_RAW_IMAGE': 'Raw',
    'GEOMETRICALLY_CORRECTED_IMAGE': 'Geomed'
    }


# files.csv columns
colFilesFileId = 0
colFilesVolume = 1
colFilesSystem = 2
colFilesCraft  = 3
colFilesTarget = 4
colFilesTime   = 5
colFilesCamera = 6
colFilesFilter = 7
colFilesNote   = 8

# centers.csv columns
colCentersFileId = 0
colCentersVolume = 1
colCentersX      = 2
colCentersY      = 3
colCentersRadius = 4 # not sure yet

# composites.csv columns
colCompositesCompositeId = 0
colCompositesFileId      = 1
colCompositesVolume      = 2
colCompositesFilter      = 3
colCompositesWeight      = 4
colCompositesX           = 5
colCompositesY           = 6

# positions.csv columns
colPositionsFileId        = 0
colPositionsDistance      = 1
colPositionsImageFraction = 2

# additions.csv columns
colAdditionsFileId     = 0
colAdditionsAdditionId = 1
colAdditionsNFrames    = 2



# Voyager PDS volumes - 87 total
voyager1jupiter = range(5101,5120+1)
voyager1saturn  = range(6101,6121+1)
voyager2jupiter = range(5201,5214+1)
voyager2saturn  = range(6201,6215+1)
voyager2uranus  = range(7201,7207+1)
voyager2neptune = range(8201,8210+1)

# list of all volumes
volumes = voyager1jupiter + voyager1saturn + voyager2jupiter + voyager2saturn + voyager2uranus + voyager2neptune
volumes = [str(volume) for volume in volumes]

# flybys = {
#     51: voyager1jupiter,
#     61: voyager1saturn,
#     52: voyager2jupiter,
#     62: voyager2saturn,
#     72: voyager2uranus,
#     82: voyager2neptune,
#     }
# # flybys = [voyager1jupiter, voyager1saturn, voyager2jupiter, voyager2saturn, voyager2uranus, voyager2neptune]

