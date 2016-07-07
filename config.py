
# voyager config options
#--------------------------------------------------------------------------------

# use like the following:
# import config
# print config.volumes


# output options
rotateImage = True

# drawBoundingBox = True
drawBoundingBox = False

# drawCrosshairs = True
drawCrosshairs = False

# use slow frame rate for first dataset
# switch to higher rate at frame 242 of set 5103
frameRate = 10 # fps
# frameRate = 15 # fps
# frameRate = 20 # fps
# frameRate = 30 # fps


# number of volumes to process for each step
nvolumesToDownload = 1
nvolumesToUnzip = 1
nvolumesToPng = 1
nvolumesToCenter = 5
nvolumesToMovieize = 6

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

downloadFolder = offlineFolder + "step1_downloads"
unzipFolder    = offlineFolder + "step2_unzips"
pngFolder      = onlineFolder  + "step3_pngs"
centeredFolder = onlineFolder  + "step4_centered"
subfolderFolder = onlineFolder  + "step5_subfolders"
coloredFolder  = onlineFolder  + "step6_colored"
framesFolder   = onlineFolder  + "step7_frames"
moviesFolder   = onlineFolder  + "step8_movies"
movieFolder    = onlineFolder  + "step9_movie"


# index file and useful columns
indexfile     = '../data/catalog/cumindex.tab'
col_filename = 2
col_craft = 4 # eg VOYAGER 1
col_phase = 5 # eg JUPITER ENCOUNTER
col_target = 6 # eg IO
col_instrument = 11 # eg WIDE ANGLE CAMERA
col_filter = 16 # eg ORANGE
col_note = 19 # eg 3 COLOR ROTATION MOVIE

# index file field value translations
translations = {
    'VOYAGER 1': 'Voyager1',
    'VOYAGER 2': 'Voyager2',
    'JUPITER ENCOUNTER': 'Jupiter',
    'WIDE ANGLE CAMERA': 'Wide',
    'NARROW ANGLE CAMERA': 'Narrow',
    }








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

