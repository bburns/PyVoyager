
# voyager config options

# use like the following:
# import config
# print config.volumes


# output options
rotate_image = True
# draw_bounding_box = True
draw_bounding_box = False
# draw_crosshairs = True
draw_crosshairs = False
frame_rate = 15 # fps


# number of volumes to process for each step
nvolumes_to_download = 2
nvolumes_to_unzip = 1
nvolumes_to_png = 1
nvolumes_to_center = 1
nvolumes_to_movieize = 1

# method of center detection
center_method = 'blob'
# center_method = 'box'

# blob detection
# binary threshold
# blob_epsilon = 0.05 # way too broad
# blob_epsilon = 0.1 # misses some dim edges of planet
blob_epsilon = 0.09

# bounding box detection
# N is the number of rows/columns to average over, for running average
# epsilon is the threshold value over which the smoothed value must cross
box_N = 5
box_epsilon = 0.2 # this is enough to ignore the dead pixel



# voyager archive url
download_url = "http://pds-rings.seti.org/archives/VGISS_{}xxx/VGISS_{}.tar.gz"

# folders for data and images
# use offline folder for large datasets (multi gigabyte)
online_folder = "C:/Users/bburns/Desktop/DeskDrawer/@voyager/@voyager/data/"
offline_folder = "C:/Users/bburns/Desktop/DeskDrawer/@voyager/@voyager/data/" #. will be f:/...

download_folder = offline_folder + "step0_downloads"
unzip_folder = offline_folder + "step1_unzips"
png_folder = online_folder + "step2_pngs"
centered_folder = online_folder + "step3_centered"
movie_folder = online_folder + "step4_movies"
combined_folder = online_folder + "step5_combined"

test_folder = 'c:/users/bburns/dropbox/docs/projects/voyager/test_cases/'


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

