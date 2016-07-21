
# voyager config options
#--------------------------------------------------------------------------------



# downloads
# ----------------------------------------

# voyager archive url
downloadUrl = "http://pds-rings.seti.org/archives/VGISS_{}xxx/VGISS_{}.tar.gz"


# images
# ----------------------------------------

# imagetype to extract using img2png
# RAW images can have overly bright backgrounds.
# CLEANED images have the riseau marks removed, but not very well.
# CALIB images have darker backgrounds, but can dim the planet too much.
# GEOMED images are corrected for geometric distortions also, but are upped to 1000x1000.
# imageType = 'RAW'
imageType = 'CALIB'
imageFilespec = "*" + imageType + ".IMG" # eg *CALIB.IMG
# imageFilespec = "*" # do all image types

# imageTypes = ['RAW', 'CLEANED', 'CALIB', 'GEOMED']
# imageTypes = ['RAW', 'CLEANED', 'CALIB']
# imageTypes = ['CLEANED', 'CALIB']
# imageTypes = ['CLEANED']
# imageTypes = ['RAW']
# imageTypes = ['CALIB']
# imageFilespecs = ["*" + imageType + ".IMG" for imageType in imageTypes]

# img2png options
# -fnamefilter - append filter name, eg _ORANGE
# -loglevel<level> - debug info
# -s<level> - scale image values by this amount - otherwise can be too dark
# note: -s10 works for uranus but blows out jupiter images -
# would need per-flyby and lots of experimenting,
# so just keep using the dim CALIB images and histogram stretching, which works well.
# img2pngOptions = "-fnamefilter -loglevel0 -s10"
img2pngOptions = "-fnamefilter -loglevel0"



# adjustments
# ----------------------------------------

adjustmentsPrefix = 'adjusted_'


# centers
# ----------------------------------------

# if you try changing these values, make sure to run `vg test`
# to see how they affect the test images

# blob detection

# level from 0.0-1.0 at which to take binary threshold for blob detection
# blobThreshold = 0.05
# blobThreshold = 0.025
# blobThreshold = 0.012 # works for most, but small triton, which has light corners
# blobThreshold = 0.015 # works for most neptune system images
blobThreshold = 255 * 0.015 # works for most neptune system images
# blobThreshold = 0.15 # try for -s10 option with uranus - worked

# area in pixels^2 at which switch from blob detection to hough circle detection
# blob detection works best for small sources - hough for bigger circles
# blobAreaCutoff = 10*10 # missed some small but sharp circles
# blobAreaCutoff = 14*14 # missed triton small but clear
# blobAreaCutoff = 20*20
# blobAreaCutoff = 24*24
blobAreaCutoff = 30*30

# canny edge detection threshold
# used by hough circle detection - lower threshold is half of this
# if this is too high then dim circles won't be detected
# but if it's too low you'd get too many spurious edges in the edge image
# 200 misses some of the dim images
# cannyUpperThreshold = 200
# the CALIB images are usually very dim
# trying to get it to recognize dim jupiters at the edges
# cannyUpperThreshold = 100
cannyUpperThreshold = 60
# no dice - the canny edges start proliferating too much, and still the jupiter edge cases aren't picked up

# prefix for centered filenames
centersPrefix = 'centered_'

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


# composites
# ----------------------------------------

# prefix for composite filenames
compositesPrefix = 'composite_'


# titles
# ----------------------------------------

titleFont = "c:/windows/fonts/!futura-light.ttf"
titleFontsize = 48



# clips
# ----------------------------------------

# filename used for clip frames
clipFilespec = 'img%05d.png'

# frame rate - frames per second
# clipFrameRate = 5 # nowork - gets stuck after a bit - why?
# clipFrameRate = 8 # nice for ariel flyby
# clipFrameRate = 10
# clipFrameRate = 12 # good for triton flyby
# clipFrameRate = 15
clipFrameRate = 20
# clipFrameRate = 25
# clipFrameRate = 30

# number of frames for title page
clipFramesForTitles = clipFrameRate * 5 #. not working right - should be 5 secs according to this

# ffmpeg options
# -y forces overwriting existing file
# -c:v specifies
# -crf specifies constant rate factor
#      see https://trac.ffmpeg.org/wiki/Encode/H.264#crf
#      0 is completely lossless, 18 is very lossless, 23 is default, 51 is worst
# Use -pix_fmt yuv420p for compatibility with outdated media players
#   (including Windows Media Player and Quicktime)
# see http://superuser.com/questions/874583/lossless-h-264-mp4-file-created-from-images-cannot-be-played-in-quicktime
clipFfmpegOptions = "-y -loglevel warning"
# clipFfmpegOutputOptions = "-c:v libx264 -pix_fmt yuv420p -crf 23"
# clipFfmpegOutputOptions = "-c:v libx264 -crf 18" # doubles size of mp4 file over crf23
# clipFfmpegOutputOptions = "-c:v libx264 -crf 23"
clipFfmpegOutputOptions = "-c:v libx264 -pix_fmt yuv420p -crf 23"


# movies
# ----------------------------------------






# files and folders
# ----------------------------------------

# convention: all folders should end with /

# folders for data and images
# use offline folder for large datasets (multi gigabyte)
onlineFolder  = "data/"
offlineFolder = "data/" # e.g. could be f:/...

downloadsFolder     = offlineFolder + "step01_downloads/"
unzipsFolder        = offlineFolder + "step02_unzips/"
imagesFolder        = onlineFolder  + "step03_images/"
adjustmentsFolder   = onlineFolder  + "step04_adjustments/"
centersFolder       = onlineFolder  + "step05_centers/"
compositesFolder    = onlineFolder  + "step06_composites/"
mosaicsFolder       = onlineFolder  + "step07_mosaics/"
targetsFolder       = onlineFolder  + "step08_targets/"
titlesFolder        = onlineFolder  + "step09_titles/"
clipsFolder         = onlineFolder  + "step10_clips/"
clipsStageFolder    = clipsFolder + 'stage/'
segmentsFolder      = onlineFolder  + "step11_segments/"
segmentsStageFolder = segmentsFolder + 'stage/'
moviesFolder        = onlineFolder  + "step12_movies/"

# test images go here
testFolder    = 'test/images/'

# database folder
dbFolder = 'db/'

# index folder
indexFolder = 'db/index/'

# useful columns in the index files
# (see db/index/readme.md)
# indexfile     = 'data/index/rawimages.tab'
indexFileColVolume = 0 # eg VGISS_5101
indexFileColFilename = 2 # eg C1389407_GEOMED.IMG
indexFileColFiletype = 3 # eg CALIBRATED_IMAGE
indexFileColCraft = 4 # eg VOYAGER 1
indexFileColPhase = 5 # eg JUPITER ENCOUNTER
indexFileColTarget = 6 # eg IO
indexFileColTime = 10 # eg 1979-03-05T15:32:56
indexFileColInstrument = 11 # eg WIDE ANGLE CAMERA
indexFileColFilter = 16 # eg ORANGE
indexFileColNote = 19 # eg 3 COLOR ROTATION MOVIE

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


# csv file databases
filesdb = dbFolder + 'files.csv'
centeringdb = dbFolder + 'centering.csv'
# centersdb = dbFolder + 'centers.csv'
compositesdb = dbFolder + 'composites.csv'
mosaicsdb = dbFolder + 'mosaics.csv'
moviesdb = dbFolder + 'movies.csv'
targetsdb = dbFolder + 'targets.csv'
frameratesdb = dbFolder + 'framerates.csv'
segmentsdb = dbFolder + 'segments.csv'


# columns in files.csv
# keep in synch with vgInitFiles.py, etc
filesColVolume = 0
filesColFileId = 1
filesColPhase = 2
filesColCraft = 3
filesColTarget = 4
filesColTime = 5
filesColInstrument = 6
filesColFilter = 7
filesColNote = 8


# columns in composites.csv
# keep in synch with vgBuildComposites.py
compositesColVolume = 0
compositesColCompositeId = 1
compositesColCenterId = 2
compositesColFilter = 3
compositesColWeight = 4



# Voyager PDS volumes - 87 total
voyager1jupiter = range(5101,5120+1)
voyager1saturn  = range(6101,6121+1)
voyager2jupiter = range(5201,5214+1)
voyager2saturn  = range(6201,6215+1)
voyager2uranus  = range(7201,7207+1)
voyager2neptune = range(8201,8210+1)

# list of all volumes
volumes = voyager1jupiter + voyager1saturn + voyager2jupiter + voyager2saturn + voyager2uranus + voyager2neptune

# flybys = {
#     # 51: voyager1jupiter,
#     51: [5104,5105],
#     61: voyager1saturn,
#     52: voyager2jupiter,
#     62: voyager2saturn,
#     72: voyager2uranus,
#     82: voyager2neptune,
#     }
# # flybys = [voyager1jupiter, voyager1saturn, voyager2jupiter, voyager2saturn, voyager2uranus, voyager2neptune]

