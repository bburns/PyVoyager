- [Goal](#goal)
- [Requirements](#requirements)
- [Installation](#installation)


## Goal

The goal is to make contributing to the project as easy as possible - so we'll be making a Docker image that contains the base PNG image files. Then users can contribute changes to the `db/*.csv` files, which control lighting, centering, alignment, framerate, annotations, etc.

The Docker image will contain png files in the `data/step03_convert` folder. Subsequent steps can be run with `vg` commands, e.g. `vg adjust 5101`. 


## Requirements

To run the complete pipeline requires Windows for the `img2png` program, which is used in the `vg convert` step. 


## Installation

You'll need Python 2.7 with pip - you can say `winget python2`, and it will install them to `C:\Python27`.

Then run `pip2 install -r requirements.txt` to install the Python dependencies. 


<!-- You'll need **Windows**, **Python 2.7**, **img2png** [2], **OpenCV** version 3 [4], **SciPy** [3], **NumPy** [5], **Matplotlib** [6], **Pillow** [8], **tabulate** [10], **more-itertools** [14], and **ffmpeg** [7]. Building one of the included .csv data files (positions.csv) requires **SpiceyPy** [11], a Python interface to **SPICE** [12].  -->

<!-- I started with an installation of **Anaconda** [9], a Python distribution with lots of pre-installed scientific libraries, including **Matplotlib**, **NumPy**, **Pillow**, and **SciPy**, and added the rest with `pip`.  -->

<!-- At this point I'm not sure how rough the installation process might be.  -->

<!-- Note that **img2png** is only available on Windows - in the future, the PNG images (or JPGs) could be hosted elsewhere for download, to skip the tarfile and extraction and conversion steps, and allow for cross-platform use, if the editing needs to be distributed. -->

For Windows, set up a Linux virtual machine -

* Install [VirtualBox][22]
* Create a VM - set disk space at least 20GB, Memory at least 1GB
* Install a 64-bit Linux distro on it (ISIS is only 64-bit), e.g. Ubuntu or Xubuntu
* Install the VirtualBox Guest Additions (for higher screen resolutions and clipboard support)

Then, starting from Ubuntu 16.04 -

<!-- (put these into an install script) -->

```bash

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


