
# voyager config options
#--------------------------------------------------------------------------------

# use like the following:
# import config
# print config.volumes


# output options
rotateImage = True

drawBoundingBox = True
# drawBoundingBox = False

drawCrosshairs = True
# drawCrosshairs = False

# frameRate = 15 # fps
frameRate = 20 # fps


# number of volumes to process for each step
nvolumesToDownload = 1
nvolumesToUnzip = 1
nvolumesToPng = 1
nvolumesToCenter = 1
nvolumesToMovieize = 1

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
onlineFolder = "C:/Users/bburns/Desktop/DeskDrawer/@voyager/@voyager/data/"
offlineFolder = "C:/Users/bburns/Desktop/DeskDrawer/@voyager/@voyager/data/" #. will be f:/...

downloadFolder = offlineFolder + "step0_downloads"
unzipFolder = offlineFolder + "step1_unzips"
pngFolder = onlineFolder + "step2_pngs"
centeredFolder = onlineFolder + "step3_centered"
movieFolder = onlineFolder + "step4_movies"
combinedFolder = onlineFolder + "step5_combined"

testFolder = 'c:/users/bburns/dropbox/docs/projects/voyager/test_cases/'


# voyager ISS volumes
voyager1jupiter = range(5101,5120)
voyager1saturn = range(6101,6121)
voyager2jupiter = range(5201,5214)
voyager2saturn = range(6201,6215)
voyager2uranus = range(7201,7207)
voyager2neptune = range(8201,8210)

flights = {
    51: voyager1jupiter,
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

