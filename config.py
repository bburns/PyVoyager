
# use like the following:
# import config
# print config.volumes


download_url = "http://pds-rings.seti.org/archives/VGISS_{}xxx/VGISS_{}.tar.gz"

#. same, for now
online_folder = "C:/Users/bburns/Desktop/DeskDrawer/@voyager/@voyager/data/"
offline_folder = "C:/Users/bburns/Desktop/DeskDrawer/@voyager/@voyager/data/"

download_folder = offline_folder + "step0_downloads"
unzip_folder = offline_folder + "step1_unzips"
png_folder = online_folder + "step2_pngs"
center_folder = online_folder + "step3_centers"
centered_png_folder = online_folder + "step4_centered_pngs"
#etc

# voyager ISS volumes
voyager1jupiter = range(5101,5120)
voyager1saturn = range(6101,6121)
voyager2jupiter = range(5201,5214)
voyager2saturn = range(6201,6215)
voyager2uranus = range(7201,7207)
voyager2neptune = range(8201,8210)

volumes = voyager1jupiter + voyager1saturn + voyager2jupiter + voyager2saturn + voyager2uranus + voyager2neptune
# volumes = [5102]

# print volumes

# nvolumes_to_download = 0
nvolumes_to_download = 1
nvolumes_to_unzip = 1
nvolumes_to_png = 1



