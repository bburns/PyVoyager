
# voyager config options
#--------------------------------------------------------------------------------

# use like the following:
# import config
# print config.volumes


# filetype to extract using img2png
filetype = 'RAW'
# imagetypes = ['RAW', 'CLEANED', 'CALIB', 'GEOMED']
# imagetype = "RAW"
# filespec = "*" + imagetype + ".img"
# filespec = "*" # do all image types

# prefix for centered filenames
centersprefix = 'centered_' 

# rotate image 180 degrees during centering step
rotateImage = True

# draw a bounding box around planet during centering step
# drawBoundingBox = True
drawBoundingBox = False

# draw crosshairs on image during centering step
# drawCrosshairs = True
drawCrosshairs = False

# use slow frame rate for first dataset
# switch to higher rate at frame 242 of set 5103
frameRate = 10 # fps
# frameRate = 15 # fps
# frameRate = 20 # fps
# frameRate = 30 # fps


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
# blobEpsilon = 0.05 # way too broad
# blobEpsilon = 0.1 # misses some dim edges of planet
blobEpsilon = 0.09

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
targetFolder     = onlineFolder  + "step7_targets"
moviesFolder     = onlineFolder  + "step8_movies"


# database folder
dbFolder = 'db'

# index folder
indexFolder = 'db/index'

# useful columns in the index files
# indexfile     = '../data/catalog/cumindex.tab'
# indexfile     = '../data/catalog/rawimages.tab'
colVolume = 0 # eg VGISS_5101
colFilename = 2 # eg C1389407_GEOMED.IMG
colFiletype = 3 # eg CALIBRATED_IMAGE
colCraft = 4 # eg VOYAGER 1
colPhase = 5 # eg JUPITER ENCOUNTER
colTarget = 6 # eg IO
colInstrument = 11 # eg WIDE ANGLE CAMERA
colFilter = 16 # eg ORANGE
colNote = 19 # eg 3 COLOR ROTATION MOVIE

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
filesdb = dbfolder + 'files.txt'
centersdb = dbfolder + 'centers.txt'
compositesdb = dbfolder + 'composites.txt'
mosaicsdb = dbfolder + 'mosaics.txt'
moviesdb = dbfolder + 'movies.txt'



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

