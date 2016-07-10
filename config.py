
# voyager config options
#--------------------------------------------------------------------------------

# use like the following:
# import config
# print config.volumes


# imagetype to extract using img2png
# RAW images can have bright backgrounds.
# CLEANED images just have the riseau marks removed.
# CALIB images have darker backgrounds, but often dim the planet too much (eg neptune).
# GEOMED images are corrected for geometric distortions also, but are upped to 1000x1000.
# imageTypes = ['RAW', 'CLEANED', 'CALIB', 'GEOMED']
imageType = 'RAW'
# imageFilespec = "*" # do all image types
imageFilespec = "*" + imageType + ".IMG" # eg *RAW.IMG

# prefix for centered filenames
centersprefix = 'centered_' 

# prefix for composite filenames
compositesPrefix = 'composite_'

# rotate image 180 degrees during centering step
rotateImage = True

# draw bounding box around biggest blob during centering step
drawBlob = False

# draw a bounding box around planet during centering step
drawBoundingBox = False

# draw crosshairs on image during centering step
drawCrosshairs = False

# use slow frame rate for first dataset
# switch to higher rate at frame 242 of set 5103
frameRate = 10 # fps
# frameRate = 15 # fps
# frameRate = 20 # fps
# frameRate = 30 # fps



# zip/tar/archive program to use
# tarProgram = 'tar'
# tarExtract = 'xf'
# tarOutput = ''
# tarProgram = '7zip'
# tarExtract = 'x'
# tarOutput = '-o'



# number of volumes to process for each step
# nvolumesToDownload = 1
# nvolumesToUnzip = 1
# nvolumesToPng = 1
# nvolumesToCenter = 5
# nvolumesToMovieize = 6

# method of center detection
# centerMethod = 'blob'
# centerMethod = 'box'
# centerMethod = 'circle'
centerMethod = 'all'

# blob detection
# binary threshold
#. could make a table of values for different volumes, or change it at different image numbers
# blobThreshold = 0.05 # way too broad
# blobThreshold = 0.1 # misses some dim edges of planet
# blobThreshold = 0.09 # try to catch dim edges of planet, works well on jupiter voy1
blobThreshold = 0.15 # works better on the failed ones which had brighter backgrounds, eg neptune
# blobThreshold = 0.20 # try for later neptune images

blobThresholds = [
    ['C0000000',0.10], # arbitrary start
    ['C0896631',0.15], # neptune bright bg
    ['C0903826',0.15], # moon, dark
    ['C0936002',0.16], # neptune brighter bg
    ['C1385455',0.09], # jupiter voy1
    ]
# blobThresholds = 




# bounding box detection
# N is the number of rows/columns to average over, for running average
# epsilon is the threshold value over which the smoothed value must cross
boxN = 5
boxEpsilon = 0.2 # this is enough to ignore the dead pixel



# voyager archive url
downloadUrl = "http://pds-rings.seti.org/archives/VGISS_{}xxx/VGISS_{}.tar.gz"

# folders for data and images
# use offline folder for large datasets (multi gigabyte)
onlineFolder  = "../data/"
offlineFolder = "../data/" #. will be f:/...
testFolder    = '../test_cases/'

downloadFolder   = offlineFolder + "step1_downloads"
unzipFolder      = offlineFolder + "step2_unzips"
imagesFolder     = onlineFolder  + "step3_images"
centersFolder    = onlineFolder  + "step4_centers"
compositesFolder = onlineFolder  + "step5_composites"
mosaicsFolder    = onlineFolder  + "step6_mosaics"
targetsFolder    = onlineFolder  + "step7_targets"
moviesFolder     = onlineFolder  + "step8_movies"


# database folder
dbFolder = 'db'

# index folder
indexFolder = 'db/index'

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



# file databases
dbfolder = 'db/'
filesdb = dbfolder + 'files.csv'
centersdb = dbfolder + 'centers.csv'
compositesdb = dbfolder + 'composites.csv'
mosaicsdb = dbfolder + 'mosaics.csv'
moviesdb = dbfolder + 'movies.csv'



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



# voyager ISS volumes
voyager1jupiter = range(5101,5120)
voyager1saturn  = range(6101,6121)
voyager2jupiter = range(5201,5214)
voyager2saturn  = range(6201,6215)
voyager2uranus  = range(7201,7207)
voyager2neptune = range(8201,8210)

flights = {
    # 51: voyager1jupiter,
    51: [5104,5105],
    61: voyager1saturn,
    52: voyager2jupiter,
    62: voyager2saturn,
    72: voyager2uranus,
    82: voyager2neptune,
    }


# list of all volumes
volumes = voyager1jupiter + voyager1saturn + voyager2jupiter + voyager2saturn + voyager2uranus + voyager2neptune
# volumes = [5102]

# flights = [voyager1jupiter, voyager1saturn, voyager2jupiter, voyager2saturn, voyager2uranus, voyager2neptune]

