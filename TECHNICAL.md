# Technical

- [Technical](#technical)
  - [Centering Images](#centering-images)
  - [Aligning Composites](#aligning-composites)
  - [Pipeline](#pipeline)
  - [Installation](#installation)
    - [For Windows, set up a Linux virtual machine](#for-windows-set-up-a-linux-virtual-machine)
    - [Starting from Ubuntu 16.04](#starting-from-ubuntu-1604)
  - [Usage](#usage)
  - [Parameters](#parameters)
  - [More details](#more-details)
  - [Testing](#testing)

## Centering Images

Images where the target fits completely in the frame are centered using [blob detection][17], [Hough circle detection][16], and [ECC Maximization][ecc]. The expected target radius is calculated through [SPICE data][12], from which the spacecraft and target position can be determined - this is used to help limit the Hough circle search, and then to draw a disc with the expected target size to which the image is aligned using ECC Maximization. The Hough circle detection is only accurate to a few pixels, so the ECC Maximization is needed for the final stabilization. 

Here are a couple of images showing the result of the centering/stabilization - the yellow circle is the expected target size:

<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1532335_centered_Orange.jpg" width="400">
<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1524138_centered_Blue.jpg" width="400">

Centering is turned off at closest approach by determining when the target size is over a threshold (e.g. when the diameter is over 80% of the image width). 


## Aligning Composites

Composite channels for closeup images are aligned using [feature detection][18] and matching, with [RANSAC][19] to eliminate outliers from a least-squares fit model for the translation (which amounts to the translation tx, ty between images being an average of the feature movements).

In more detail, 'interesting' features are detected using [ORB][20] in one image, and matched with their corresponding point in another image. This is done for dozens-hundreds of interest points - they are each described with a feature vector, also obtained by ORB, then matched up with their corresponding point by a brute-force search. The RANSAC algorithm is used to throw out outliers, which would otherwise throw off the determined average translation. 

If this approach fails to find a good translation (due to lack of enough corresponding points, for instance), it will fall back on [ECC Maximization][ecc] to try to align the images. 

Here is an image showing what the feature-matching process looks like, and the resulting combined image (with enhanced contrast). 

<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1637948_matching.jpg" width="800">
<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1637948_aligned.jpg" width="400">


## Pipeline

Voyager consists of a command line interface to a pipeline of Python programs with the following steps (some in progress):

* Download - download archives from [PDS EDR (raw) archives][1]
* Unzip - decompress archive volumes to IMQ files
<!-- * Convert - convert RAW images to pngs using [img2png][img2png] -->
<!-- * Adjust - rotate180, histogram stretch -->
* Import - import IMQ files to ISIS cube files, attach SPICE geometry data with `spiceinit`
* Adjust - rotate 180 degrees, calibrate images
* Flatfield - subtract good flatfields (dark images)
* Dereseau - remove reseau marks cleanly (set to null)
* Denoise - identify/eliminate noise where possible (set to null)
* Inpaint - fill in missing information with pixels from prior frame or average of surrounding pixels - be careful with reseau marks on limbs of target
<!-- * Undistort - geometric correction using reseau marks 800x800->1000x1000 -->
* Center - center and stabilize images where entire target is visible
* Map - project image to cylindrical map using SPICE information, fit there with ISIS jigsaw to refine pointing information
* Colorize - colorize images by pulling missing channels from the map
<!-- * Composite - combine channels -->
<!-- * Mosaic - combine images using auto+manual info -->
* Crop - crop and zoom frames, e.g. volcanoes on Io
* Annotate - add caption information, point out features, etc.
<!-- * Clips - combine images into short movies, one per target -->
* Movies - combine images into movies, add music


## Installation

<!-- You'll need **Windows**, **Python 2.7**, **img2png** [2], **OpenCV** version 3 [4], **SciPy** [3], **NumPy** [5], **Matplotlib** [6], **Pillow** [8], **tabulate** [10], **more-itertools** [14], and **ffmpeg** [7]. Building one of the included .csv data files (positions.csv) requires **SpiceyPy** [11], a Python interface to **SPICE** [12].  -->

<!-- I started with an installation of **Anaconda** [9], a Python distribution with lots of pre-installed scientific libraries, including **Matplotlib**, **NumPy**, **Pillow**, and **SciPy**, and added the rest with `pip`.  -->

<!-- At this point I'm not sure how rough the installation process might be.  -->

<!-- Note that **img2png** is only available on Windows - in the future, the PNG images (or JPGs) could be hosted elsewhere for download, to skip the tarfile and extraction and conversion steps, and allow for cross-platform use, if the editing needs to be distributed. -->

### For Windows, set up a Linux virtual machine

* Install [VirtualBox][22]
* Create a VM - set disk space at least 20GB, Memory at least 1GB
* Install a 64-bit Linux distro on it (ISIS is only 64-bit), e.g. Ubuntu or Xubuntu
* Install the VirtualBox Guest Additions (for higher screen resolutions and clipboard support)

### Starting from Ubuntu 16.04

<!-- (put these into an install script) -->

``` bash

# set a location for applications, e.g. ~/Apps
mkdir ~/Apps
export APPS=~/Apps

# install PyVoyager
# (if using a virtual machine, can install on Windows instead so can access the image files from there also)
cd $APPS
git clone https://github.com/bburns/PyVoyager.git

# install CSPICE (C language version of SPICE)
# see https://naif.jpl.nasa.gov/naif/toolkit_C_PC_Linux_GCC_64bit.html
cd $APPS
wget http://naif.jpl.nasa.gov/pub/naif/toolkit//C/PC_Linux_GCC_64bit/packages/cspice.tar.Z
wget http://naif.jpl.nasa.gov/pub/naif/toolkit//C/PC_Linux_GCC_64bit/packages/importCSpice.csh
/bin/csh -f importCSpice.csh
rm cspice.tar.Z
rm importCSpice.csh

## install Java, for the ISIS installer
#sudo apt install default-jre
#sudo add-apt-repository ppa:webupd8team/java
#sudo apt update
#sudo apt install oracle-java8-installer

# install ISIS
cd $APPS
wget https://isis.astrogeology.usgs.gov/documents/InstallGuide/assets/isisInstall.sh
chmod +x isisInstall.sh
mkdir Isis
./isisInstall.sh -n -d $APPS/Isis

# add to .profile:
export APPS=~/Apps
export PYVOYAGER=$APPS/PyVoyager
export SPICEROOT=$APPS/cspice
export ISISROOT=$APPS/Isis/isis
. $ISISROOT/scripts/isis3Startup.sh

source ~/.profile


# build camrotate
#. or just include the binary - is it static?

# get some libraries for building ISIS programs
$ sudo apt install libxerces-c-dev
$ sudo apt install libsuperlu-dev

# change a line in $ISISROOT/make/config.linux-x86_64 as I couldn't get it to
# recognize superlu4 as superlu4.3. superlu4.3 isn't available yet as a package - 
# it would require compiling it from source, which I didn't want to get into. 
# not sure if any ISIS programs need the 4.3 version. 
from 
SUPERLULIB    = -lsuperlu_4.3 -lblas -lgfortran
to 
SUPERLULIB    = -lsuperlu -lblas -lgfortran

# comment out a couple of lines in $ISISROOT/inc/SpecialPixel.h to turn off
# some unused variable warnings - couldn't get pragma diagnostic to work
line 101   // const double ValidMinimum   = IVALID_MIN8.d;
line 162   // const int IVALID_MAX4  = (*((const int *) &VALID_MAX4));

# make the program
cd $PYVOYAGER/src/camrotate
. setpaths.sh
make

#. add camrotate to PATH


# get Voyager SPICE kernels locally
pushd $ISIS3DATA
rsync -avz --partial --progress --delete isisdist.wr.usgs.gov::isis3data/data/voyager1 .
rsync -avz --partial --progress --delete isisdist.wr.usgs.gov::isis3data/data/voyager2 .
popd

# get some different Voyager 1 and Jupiter SPICE SPK kernels
#. could just add these to git
mkdir ~/PyVoyager/kernels/spk
pushd ~/PyVoyager/kernels/spk
wget ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/jup100.bsp
wget ftp://naif.jpl.nasa.gov/pub/naif/VOYAGER/kernels/spk/Voyager_1.a54206u_V0.2_merged.bsp
popd


# get some libraries for ISIS (don't need if using earlier Ubuntu, e.g. 12.04)

## libblas3gf
wget http://mirrors.kernel.org/ubuntu/pool/main/b/blas/libblas3gf_1.2.20110419-2ubuntu1_amd64.deb
sudo dpkg -i libblas3gf_1.2.20110419-2ubuntu1_amd64.deb

## libjpeg62
sudo apt install libjpeg62

## libvpx
wget http://ftp.us.debian.org/debian/pool/main/libv/libvpx/libvpx1_1.3.0-3_amd64.deb
sudo dpkg -i libvpx1_1.3.0-3_amd64.deb


# install OpenCV version 3
## (Ubuntu package is version 2)
## sudo apt install libopencv-dev
sudo apt install build-essential
sudo apt install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

cd $APPS
wget https://github.com/Itseez/opencv/archive/3.1.0.zip
unzip 3.1.0.zip
rm 3.1.0.zip
cd opencv-3.1.0
mkdir release
cd release
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
cd ..
make
sudo make install
## release is >2gb, so remove it
rmdir release
## can keep opencv-3.1.0 around though, as contains source code
cd ~

# get some Python libraries
# Python 2.7 is included with Ubuntu

## pip
sudo apt install python-pip
sudo pip install --upgrade pip

## numpy, scipy, matplotlib
sudo apt install python-numpy python-scipy python-matplotlib

## cv2 (OpenCV Python interface)
sudo apt install python-opencv

## SpiceyPy (SPICE Python interface)
sudo pip install spiceypy

## miscellaneous
sudo pip install tabulate
sudo pip install more_itertools
sudo pip install python-dateutil


# get some other commands

## make a beep sound
sudo apt install beep

## convenient way to run batch commands
sudo apt install parallel

## image viewer, e.g. for jpegs
sudo apt install eog

```


## Usage

Entering `vg` will show the available commands:

    PyVoyager commands

      vg download       - download volume(s)
      vg unzip          - unzip volume(s)
      vg convert        - convert IMGs to PNGs
      vg adjust         - adjust images (rotate and enhance)
      vg denoise        - remove noise from images
      vg center         - center images
      vg inpaint        - fill in missing pixels where possible
      vg composite      - create color images
      vg target         - copy images into target subfolders
      vg clips          - create bw or color clips
      vg movies         - create movies from clips
      vg list           - show status of local datasets

      vg test center    - run centering tests
      vg test denoise   - run denoising tests

    where most commands can be followed by <filter> and <options>, where

      <filter>     = [<volnums>] [<imageIds>] [<targetpath>]
                     (all are anded together)
      <volnums>    = 5101..5120 Voyager 1 Jupiter
                     6101..6121 Voyager 1 Saturn
                     5201..5214 Voyager 2 Jupiter
                     6201..6215 Voyager 2 Saturn
                     7201..7207 Voyager 2 Uranus
                     8201..8210 Voyager 2 Neptune
                     (ranges and wildcards like 5101-5104 or 51* are ok)
      <imageIds>   = imageId or range, like C1234567, C1234567-C1234569
      <targetpath> = [<system>]/[<spacecraft>]/[<target>]/[<camera>]
      <system>     = Jupiter|Saturn|Uranus|Neptune
      <spacecraft> = Voyager1|Voyager2
      <target>     = Jupiter|Io|Europa|, etc.
      <camera>     = Narrow|Wide
      <options>    = -y overwrite existing volume data

    e.g. vg clips 8205 //triton

Most commands will fill in any missing intermediate steps, so for example, to download, denoise, center, infill, composite, mosaic, and annotate all the Uranus images (which might take a while - there are 7 volumes of 1-3GB each), enter

    > vg annotate 7*

Or you can be more explicit and run them individually, as follows (and note, many steps are optional, like denoise, infill, mosaic, annotate - though might need to tweak the code to turn off the automatic running of previous step) -

Download a tarfile volume, e.g. volume 5101 - the first dataset, Jupiter approach

    > vg download 5101

Unzip the tarfile

    > vg unzip 5101

Convert the IMG files to PNGs with [img2png][img2png]

    > vg convert 5101

Adjust the contrast levels and rotate the images

    > vg adjust 5101

Remove noise where possible

    > vg denoise 5101

Center the images on the main body in the images

    > vg center 5101

Colorize the images

    > vg composite 5101

Annotate the images

    > vg annotate 5101

Then you can make short movies of all the downloaded datasets, organized by planet/spacecraft/target/camera (this step must be performed in an Admin console, because it uses `mklink` to make symbolic links, which require elevated privileges)

    > vg clips [targetpath]

e.g.

    > vg clips //triton/narrow

to generate the narrow angle Triton flyby movies, or

    > vg clips

to generate all available movies.

Then these clips can be assembled into movies (one per system and then one overall movie, as specified in db/movies.csv) with

    > vg movies

Use the `vg list [volnums]` command to keep track of what stages different volumes are at, e.g.:

      Volume  Download    Unzip    Convert   Adjust    Center    Composite
    --------  ----------  -------  --------  --------  --------  -----------
        5101  x           x        x
        5102  x           x        x
        5103  x           x        x
        5201  x           x        x         x         x         x
        6201  x           x
        7201  x           x
        7202  x           x


## Parameters

All configuration settings are stored in `config.py` - the goal is for the same set of parameters to work across all datasets as much as possible.


## More details

<!-- (Update this) -->

The data for each step is put into the following folders in the `data` subfolder:

    step01_download
    step02_unzip
    step03_import

There are 87 PDS volumes for all the Voyager images, each ~1-3GB, as described [here](http://pds-rings.seti.org/voyager/iss/calib_images.html).

Each image comes in 4 formats - RAW, CLEANED, CALIB, and GEOMED.

- RAW images are the least processed images available - they're 800x800 pixels, and include the reseau marks (the grid of dots) used for calibration.
- CLEANED images have had the reseau marks removed, but leave noticeable artifacts that look like volcanoes on the limbs of planets.
- CALIB images have had dark images subtracted from the CLEANED images, and
- GEOMED are the CALIB images geometrically corrected and projected to 1000x1000 pixels.

Ideally the RAW images would be used with a better reseau removal algorithm, but for now the CALIB images are used.

After downloading the tar.gz files, unzipping them, extracting the PNGs, adjusting and denoising them, the CALIB images are centered based on blob detection, Hough circle detection, the expected target radius, and [ECC maximization][ecc] for stabilization. See the section on centering below for more details. 

The expected radius of the target is determined in advance by the `vg init positions` command, which uses SPICE position data, target position, target size, and camera FOV to determine size of target in image, which is stored in `db/positions.csv` (included in the distribution). This helps with the Hough circle detection, and also to stabilize the image. 

The PDS volumes come with index files for all the images they contain, which have been compiled into one smaller file using `vg init files`. The resulting file (`db/files.csv`, included with the distribution) looks like this:

    fileid,volume,phase,craft,target,time,instrument,filter,note
    C1541422,5104,Jupiter,Voyager1,Jupiter,1979-02-01T00:37:04,Narrow,Blue,3 COLOR ROTATION MOVIE
    C1541424,5104,Jupiter,Voyager1,Jupiter,1979-02-01T00:38:40,Narrow,Orange,3 COLOR ROTATION MOVIE
    C1541426,5104,Jupiter,Voyager1,Jupiter,1979-02-01T00:40:16,Narrow,Green,3 COLOR ROTATION MOVIE
    ...

though different targets and camera records can be also interleaved with others.

One issue is that some images have more than one target in them (e.g. Jupiter with Io) - in the PDS index these images are listed with just one target. For now, you can change which target the image gets sorted under by editing the `db/targets.csv` file - in the future it could be enhanced to also split the image into two records so each target can be included in the appropriate movie. One retargeting that is performed in advance is from rings to their planet - otherwise the rings would show up in separate movies.

The master list of files (`db/files.csv`) has been compiled into a list of composite frames to build using the `vg init composites` command, based on repeating groups of filters for the different targets and cameras. The resulting file (`db/composites.csv`) looks like this:

    compositeId,centerId,volume,filter
    C1541422,C1541422,5104,Blue
    C1541422,C1541424,5104,Orange
    C1541422,C1541426,5104,Green

This file is used by the `vg composite <volume>` command to generate the color frames.

The clips are generated with the `vg clips [targetpath]` command, which links all the images into target subfolders (arranged by planet/spacecraft/target/camera), numbering them sequentially, and running [ffmpeg][ffmpeg] to generate an mp4 clip for each. The target size is also used to control the speed of the movie, slowing down when the target is closer, but the framerate can also be controlled via the `framerateConstants.csv` and `framerates.csv` files. 

The `vg movies` command then concatenates all available clips into movies, using the order specified in `db/movies.csv`. 


## Testing

Some centering test images are included in the `test/center` folder, and their correct center values in `test/testCenterFiles.csv`. You can run the tests on them with `vg test center`. The goal is to include some easy targets and lots of edge cases to test the centering/stabilizing routines.

Denoising test images are located in `test/denoise` - you can run the tests with `vg test denoise` - check the results in the same denoise folder.



[isis]: https://isis.astrogeology.usgs.gov/
[img2png]: http://www.mmedia.is/bjj/utils/img2png/
[ffmpeg]: https://ffmpeg.org/
[ecc]: http://xanthippi.ceid.upatras.gr/people/evangelidis/ecc/

[1]: http://pds-rings.seti.org/voyager/
[3]: https://www.scipy.org/
[4]: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#cv2.HoughCircles
[5]: http://www.numpy.org/
[6]: http://matplotlib.org/
[8]: https://python-pillow.org/
[9]: https://www.continuum.io/downloads
[10]: https://pypi.python.org/pypi/tabulate
[11]: https://github.com/AndrewAnnex/SpiceyPy
[12]: http://naif.jpl.nasa.gov/naif/
[13]: https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/
[14]: https://github.com/erikrose/more-itertools
[16]: https://en.wikipedia.org/wiki/Circle_Hough_Transform
[17]: https://en.wikipedia.org/wiki/Blob_detection
[18]: https://en.wikipedia.org/wiki/Feature_detection_(computer_vision)
[19]: https://en.wikipedia.org/wiki/RANSAC
[20]: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_orb/py_orb.html
[22]: https://www.virtualbox.org/
