
# voyager config options
#--------------------------------------------------------------------------------

# use like the following:
# import config
# print config.volumes


# debugging
# ----------------------------------------

debugImages = False



# downloads
# ----------------------------------------

# voyager archive url
downloadUrl = "http://pds-rings.seti.org/archives/VGISS_{}xxx/VGISS_{}.tar.gz"


# images
# ----------------------------------------

# imagetype to extract using img2png
# RAW images can have overly bright backgrounds.
# CLEANED images have the riseau marks removed.
# CALIB images have darker backgrounds, but can dim the planet too much.
# GEOMED images are corrected for geometric distortions also, but are upped to 1000x1000.
# imageType = 'RAW'
# imageType = 'CLEANED'
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
#. add multiplication level
# img2pngOptions = "-fnamefilter" # append filter name, eg _ORANGE
# -fnamefilter - append filter name, eg _ORANGE
# -loglevel0 - not so much info
img2pngOptions = "-fnamefilter -loglevel0" 


# centers
# ----------------------------------------

# method of center detection
#. ditch - just handle through code
# centerMethod = 'blob'
# centerMethod = 'circle'
centerMethod = 'all'

#. ditch
# blobAreaDerivativeMax = -0.02


# blob detection

# level from 0.0-1.0 at which to take binary threshold for blob detection
# blobThreshold = 0.05
# blobThreshold = 0.025 
blobThreshold = 0.015
# blobThreshold = 0.012 # (* 255 0.012)=3 # works for most, but small triton, which has light corners

# area in pixels^2 at which switch from blob detection to hough circle detection
# blob detection works best for small sources - hough for bigger circles
# blobAreaCutoff = 10*10 # missed some small but sharp circles
# blobAreaCutoff = 14*14 # missed triton small but clear
# blobAreaCutoff = 20*20
# blobAreaCutoff = 24*24
blobAreaCutoff = 30*30

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
drawBinaryImage = False # save thresholded image
drawBoundingBox = False # draw bounding box around biggest blob
drawEdges = False # save canny edges image ~ used by hough circle detector
drawCircle = False # draw best detected hough circle
drawCircles = False # draw all detected hough circles
drawCrosshairs = False # draw crosshairs on image


# composites
# ----------------------------------------

# prefix for composite filenames
compositesPrefix = 'composite_'


# titles
# ----------------------------------------

titleFont = "c:/windows/fonts/!futura-light.ttf"
titleFontsize = 48



# movies
# ----------------------------------------

# filename used for movie frames
movieFilespec = 'img%05d.png'

# frame rate - frames per second
#. need to set this per target
# movieFrameRate = 5 # nowork - gets stuck after a bit
movieFrameRate = 12 # good for triton flyby
# movieFrameRate = 15
# movieFrameRate = 20
# movieFrameRate = 30

# number of duplicate frames to include for slow parts of movie
# movieFramesForSlowParts = 5
movieFramesForSlowParts = 8

# number of frames for title page
movieFramesForTitles = movieFrameRate * 5



# files and folders
# ----------------------------------------

# convention: all folders should end with /

# folders for data and images
# use offline folder for large datasets (multi gigabyte)
onlineFolder  = "data/"
offlineFolder = "data/" # e.g. could be f:/...

downloadFolder   = offlineFolder + "step1_downloads/"
unzipFolder      = offlineFolder + "step2_unzips/"
imagesFolder     = onlineFolder  + "step3_images/"
centersFolder    = onlineFolder  + "step4_centers/"
compositesFolder = onlineFolder  + "step5_composites/"
mosaicsFolder    = onlineFolder  + "step6_mosaics/"
targetsFolder    = onlineFolder  + "step7_targets/"
titlesFolder    = onlineFolder  + "step8_titles/"
moviesFolder     = onlineFolder  + "step9_movies/"

# test images go here
testFolder    = 'test/images/'

# database folder
dbFolder = 'db/'

# index folder
indexFolder = 'db/index/'

# useful columns in the index files
# (see db/index/readme.md)
# indexfile     = '../data/catalog/cumindex.tab'
# indexfile     = '../data/catalog/rawimages.tab'
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
    'GEOMETRICALLY_CORRECTED_IMAGE': 'Geomed',
    }


# csv file databases
filesdb = dbFolder + '/files.csv'
centersdb = dbFolder + '/centers.csv'
compositesdb = dbFolder + '/composites.csv'
mosaicsdb = dbFolder + '/mosaics.csv'
moviesdb = dbFolder + '/movies.csv'


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
    


# # voyager ISS volumes
# voyager1jupiter = range(5101,5120)
# voyager1saturn  = range(6101,6121)
# voyager2jupiter = range(5201,5214)
# voyager2saturn  = range(6201,6215)
# voyager2uranus  = range(7201,7207)
# voyager2neptune = range(8201,8210)

# flights = {
#     # 51: voyager1jupiter,
#     51: [5104,5105],
#     61: voyager1saturn,
#     52: voyager2jupiter,
#     62: voyager2saturn,
#     72: voyager2uranus,
#     82: voyager2neptune,
#     }


# # list of all volumes
# volumes = voyager1jupiter + voyager1saturn + voyager2jupiter + voyager2saturn + voyager2uranus + voyager2neptune
# # volumes = [5102]

# # flights = [voyager1jupiter, voyager1saturn, voyager2jupiter, voyager2saturn, voyager2uranus, voyager2neptune]

