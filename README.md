
PyVoyager
========================================

Version 0.43 inprogress

PyVoyager automatically creates and stabilizes Voyager flyby movies - the eventual goal is to produce a single movie with titles and audio as automatically as possible, with each planet and target having a separate segment. Ideally the movie would also include some mosaics generated with hand-annotated data, and/or separately hand-assembled mosaics of better quality.

This is a large project, so it's designed to be split up among different people working on different segments, coordinated through .csv files. 

It's in an early stage of development, but is still usable for downloading and extracting datasets, and assembling rough movies. I'm working on improving the centering/stabilization and coloring routines.

There are a total of 70k+ images in the Voyager archives - the datasets are rather large - 1-3GB per compressed volume, with 87 volumes in total, so there is a lot to explore.

You can read more about the Planetary Data System (PDS) which hosts the archives here - http://www.planetary.org/explore/space-topics/space-imaging/data.html.


Example Movies
----------------------------------------

These movies are still in early stages, so pardon the jitters and the mini 'volcanoes' (leftover from removal of reseau marks).

https://www.youtube.com/watch?v=JuL3hSbp7Yc  
Voyager 2 Uranus system flyby in color and black and white v0.40 (5 mins)

https://www.youtube.com/watch?v=rAGWBo3-J2E  
Voyager 1 Jupiter rotation movie color v0.41

https://www.youtube.com/watch?v=kcJB9rNzCH4  
Voyager 2 Triton flyby v0.32

https://www.youtube.com/watch?v=VF3UCo2P-4Y  
Voyager 2 Neptune flyby v0.2 - note Triton orbiting Neptune in a retrograde direction

https://www.youtube.com/watch?v=c8O2BKqM0Qc  
Voyager 2 Neptune flyby color v0.2 - automatically colorized version

https://www.youtube.com/watch?v=o4zh8C-ma_A  
Voyager 1 Jupiter approach v0.1 - (RAW images with reseau marks)


What you can do
----------------------------------------

Although the goal is to complete the movies in as automated fashion as possible, there are still places where manual intervention is required - 

- Some frames don't get centered correctly due to noise, or being on the edge of an image, etc., so they need to be manually centered by editing the `db/centersOverride.csv` file, or (eventually) using the `vg center <imageId> <x offset>, <y offset>` command.
- Centering needs to be manually turned off at close approach and back on again at departure - this is done in `db/centering.csv`. 
- Multi-target images often need to be relabelled to the largest target in the image (or whatever the centering routines center on) - this is done in the `db/retargeting.csv` file.
- Close-up composite images need to be manually aligned - e.g. the closeups of the clouds of Jupiter, by editing the `db/composites.csv` file. The weight of the different filters can also be adjusted there. 
- Movie frame rates need to be adjusted so interesting images stay on the screen longer - this is done in the `db/framerates.csv` file. 
- And eventually, mosaics would need to be specified manually in a `db/mosaics.csv` file. 


Pipeline
----------------------------------------

Voyager consists of a command line interface to a pipeline of Python programs with the following steps:

* Download Voyager datasets from **PDS archives** [1]
* Extract the contents of the tar.gz archives
* Convert Voyager IMG images to PNGs using **img2png** [2]
* Adjust the contrast of the images and rotate them
* Center images on the target using blob detection using **SciPy** [3] and Hough circle detection using **OpenCV** [4]. Other libraries used include **NumPy** [5] and **Matplotlib** [6]
* Stabilize the images with ECC Maximization [13] in **OpenCV**
* Colorize frames by combining images, where possible, using **OpenCV**
* [Build mosaics from images with hand-annotated information]
* Arrange images into folders corresponding to different planets/spacecrafts/targets/cameras
* Make movies for each target flyby and add titles [and music] using **ffmpeg** [7] and **Pillow** [8]


Installation
----------------------------------------

You'll need **Windows**, **Python 2.7**, **img2png** [2], **OpenCV** version 3 [4], **SciPy** [3], **NumPy** [5], **Matplotlib** [6], **Pillow** [8], **tabulate** [10], **more-itertools** [14], and **ffmpeg** [7]. Building one of the included .csv data files (positions.csv) requires **SpiceyPy** [11], a Python interface to **SPICE** [12]. 

I started with an installation of **Anaconda** [9], a Python distribution with lots of pre-installed scientific libraries, including **Matplotlib**, **NumPy**, **Pillow**, and **SciPy**. 

At this point I'm not sure how rough the installation process might be - eventually I'll make some step-by-step instructions. 


Compatibility
----------------------------------------

The main limitation is **img2png**, which is only available on Windows - this is what converts the PDS IMG files to PNGs, so it's an important step.

In the future, the PNG images (or JPGs) could be hosted elsewhere for download, to skip the tarfile and extraction and conversion steps, and allow for cross-platform use.


Usage
----------------------------------------

Entering `vg` will show the available commands:

    Voyager commands

      vg download <volnums>             - download volume(s)
      vg unzip <volnums>                - unzip volume(s)
      vg convert <volnums>              - convert IMGs to PNGs
      vg center <volnums>               - center images
      vg composite <volnums>            - create color images
      vg target <volnums>               - copy images into target subfolders
      vg list                           - show status of local datasets
      vg clips bw|color [<targetpath>]  - create bw or color movies of flybys
      vg movies                         - combine clips into movies

    where

      <volnums> = 5101..5120 Voyager 1 Jupiter
                  6101..6121 Voyager 1 Saturn
                  5201..5214 Voyager 2 Jupiter
                  6201..6215 Voyager 2 Saturn
                  7201..7207 Voyager 2 Uranus
                  8201..8210 Voyager 2 Neptune
                  (ranges and wildcards like 5101-5104 or 51* are ok)

      <targetpath> = [<system>]/[<spacecraft>]/[<target>]/[<camera>]
      <system>     = Jupiter|Saturn|Uranus|Neptune
      <spacecraft> = Voyager1|Voyager2
      <target>     = Jupiter|Io|Europa|, etc.
      <camera>     = Narrow|Wide

    e.g. vg movies bw //Triton

    You can also add `-y` to a command to have it overwrite any existing data.

Most commands will fill in any missing intermediate steps, so for example, to download and composite all the Uranus images (might take a while - there are 7 volumes of 1-3GB each), enter

    > vg composite 7*

Or you can be more explicit and run them individually, as folllows -

Download a tarfile volume, e.g. volume 5101 - the first dataset, Jupiter approach

    > vg download 5101

Unzip the tarfile

    > vg unzip 5101

Convert the IMG files to PNGs with **img2png**

    > vg convert 5101

Adjust the contrast levels and rotate the images

    > vg adjust 5101

Center the images on the main body in the images

    > vg center 5101

Colorize the images

    > vg composite 5101

or do all of these steps automatically (performs all missing steps)

    > vg composite 5101

Then you can make b&w or color movies of all the downloaded datasets, organized by planet/spacecraft/target/camera (this step must be performed in an Admin console, because it uses `mklink` to make symbolic links, which require elevated privileges)

    > vg clips bw|color [targetpath]

e.g.

    > vg clips bw //Triton

to generate the Triton flyby movies (both Narrow and Wide angle cameras), or

    > vg clips color

to generate all available color movies.

Then these clips can be assembled into movies (one per system and then one overall movie, as specified in db/movies.csv) with

    > vg movies

Use the `vg list` command to keep track of what stages different volumes are at:

      Volume  Downloads    Unzips    Images    Adjustments    Centers    Composites
    --------  -----------  --------  --------  -------------  ---------  ------------
        5101  x            x         x
        5102  x            x         x
        5103  x            x         x
        5201  x            x         x         x              x          x
        6201  x            x
        7201  x            x
        7202  x            x


Parameters
----------------------------------------

All configuration settings are stored in `config.py` - the goal is for the same set of parameters to work across all datasets and avoid adding more specification files, though it might be necessary to specify some parameters per volume. 

There are 12 parameters that control the centering and stabilization routines - 

    blobThreshold = 4
    blobAreaCutoff = 30*30
    
    cannyUpperThreshold = 60
    
    houghParameterSpace = 1
    houghAccumulatorThreshold = 200
    houghMinRadius = 1
    houghMaxRadius = 2

    stabilizeMaxRadiusDifference = 20
    stabilizeMaxDeltaPosition = 18
    stabilizeECCIterations = 5000
    stabilizeECCTerminationEpsilon = 1e-10
    stabilizeNTimesFixedFrameUsed = 10


How it works
----------------------------------------

The data for each step is put into the following folders in the `data` subfolder:

    step01_downloads
    step02_unzips
    step03_images
    step04_adjustments
    step05_centers
    step06_composites
    step07_mosaics
    step08_targets
    step09_titles
    step10_clips
    step11_movies

There are 87 PDS volumes for all the Voyager images, each ~1-3GB, as described here http://pds-rings.seti.org/voyager/iss/calib_images.html.

Each image comes in 4 formats - RAW, CLEANED, CALIB, and GEOMED.

- RAW images are the least processed images available - they're 800x800 pixels, and include the reseau marks (the grid of dots) used for calibration.
- CLEANED images have had the reseau marks removed, but leave noticeable artifacts that look like volcanoes on the limbs of planets.
- CALIB images have had dark images subtracted from the CLEANED images, and
- GEOMED are the CALIB images geometrically corrected and projected to 1000x1000 pixels.

Ideally the RAW images would be used with a better reseau removal algorithm, but for now the CALIB images are used.

After downloading the tar files, unzipping them, and extracting the PNGs, the CALIB images are centered based on blob detection and Hough circle detection. This works for most cases, but there is still some jitter on frames where it doesn't work very well, so this has room for improvement.

There are several cases that need to be handled:

1. small/point-like targets
2. 'normal' full-circle targets
3. targets with gaps
4. targets with centers outside of the image
5. crescents
6. targets larger than the field of view
7. edge defects which the blob detector picks up need to be ignored

The small/point-like targets are handled fairly well by the blob detection routine. Where the area is larger than some small value though, eg 15x15 pixels, the detection is better handled by the Hough circle detector, which works well on the 'normal' circular targets and targets with gaps.

But the Hough detector doesn't handle targets with centers outside of the image, as it assumes otherwise, and it also doesn't work too well with crescents, as they are basically two partial circles, so there can be some jitters in the movies. Those two cases are not well-accounted for at the moment.

Targets larger than the field of view must be handled specially, as the blob and Hough detectors will pick up spurious features to center on. So a file `db/centering.csv` is set up to tell the centering routine when to turn centering off then back on after closest approach, based on the image name. This must be set up manually, and looks like this -

    planetCraftTargetCamera,centeringOff,centeringOn
    Neptune-Voyager2-Neptune-Narrow,C1127459,C1152407
    Neptune-Voyager2-Neptune-Wide,C1137509,C1140815
    Neptune-Voyager2-Triton-Narrow,C1139255,C1140614

The alternative would be to base this more automatically on distance from the planet and angular radius, but that might be a future enhancement - it would also allow for a gradual slow-down around closest approach.

The Hough circle detector is not sensitive enough to produce very stable movies, so another step is performed to stabilize each frame with respect to the last stable frame. The technique is called ECC Maximization [13]. This step is part of the `vg center` command.

The PDS volumes come with index files for all the images they contain, which have been compiled into one smaller file using `vg init files`. The resulting file (`db/files.csv`) looks like this:

    volume,fileid,phase,craft,target,time,instrument,filter,note
    5104,C1541422,Jupiter,Voyager1,Jupiter,1979-02-01T00:37:04,Narrow,Blue,3 COLOR ROTATION MOVIE
    5104,C1541424,Jupiter,Voyager1,Jupiter,1979-02-01T00:38:40,Narrow,Orange,3 COLOR ROTATION MOVIE
    5104,C1541426,Jupiter,Voyager1,Jupiter,1979-02-01T00:40:16,Narrow,Green,3 COLOR ROTATION MOVIE
    ...

though different targets and camera records can be also interleaved with others.

One issue is that some images have more than one target in them (e.g. Jupiter with Io) - in the PDS index these images are listed with just one target. For now, you can change which target the image gets sorted under by editing the `db/targets.csv` file - in the future it could be enhanced to also split the image into two records so each target can be included in the appropriate movie. One retargeting that is performed in advance is from rings to their planet - otherwise the rings would show up in separate movies.

The master list of files (`db/files.csv`) has been compiled into a list of composite frames to build using the `vg init composites` command, based on repeating groups of filters for the different targets and cameras. The resulting file (`db/composites.csv`) looks like this:

    volume,compositeId,centerId,filter
    5104,C1541422,C1541422,Blue
    5104,C1541422,C1541424,Orange
    5104,C1541422,C1541426,Green

This file is used by the `vg composites <volume>` command to generate the color frames.

The clips are generated with the `vg clips bw|color [targetpath]` command, which links all the images into target subfolders (arranged by planet/spacecraft/target/camera), renumbering them sequentially, and running **ffmpeg** to generate an mp4 clip for each.

Here is how black and white vs color clips are generated -

    Adjusted   Centered     Composite    Notes
    ------------------------------------------------------------------
    [ ]        [ ]\         [ ]          centered 3 color composite
    [ ]        [ ] |-------/
    [ ]        [ ]/
    [ ]        [ ]----------[ ]          centered bw
    [ ]        [ ]\_________[ ]          centered 2 color composite
    [ ]        [ ]/
    [ ]---------------------[ ]          uncentered bw
    [ ]\                    [ ]          uncentered 3 color composite
    [ ] -------------------/
    [ ]/
    [ ]        [ ]----------[ ]          centered bw
    [ ]        [ ]----------[ ]          centered bw
    \------------/           |
       bw clips         color clips

The `vg movies` command then concatenates all available clips into movies, using the order specified in `db/movies.csv`. 

That's about it!


Testing
----------------------------------------

Some test images are included in the `test/images` folder, and their correct bounding box values, where known, in `test/testfiles.csv`. You can run the tests on them with `cd test` and `python testCentering.py`. The goal is to include some easy targets and lots of edge cases to test the centering routines. If you find a frame that doesn't center correctly you can put the original image into the images folder and add a record to testfiles.csv.


Issues
----------------------------------------

There's a Trello board to track issues and progress here - https://trello.com/b/kEkGDMYR/voyager


Next steps
----------------------------------------

* Improve stabilization/centering routines - handle off-screen centers and crescents
* Improve color frame detection and rendering routines - borrow missing channels from previous frames, use all available channels, use more precise colors than rgb, increase color saturation, colorize target consistently, eg with a large reference view (eg nice blue neptune globe), add hand-annotation for alignment where necessary
* Add audio
* Host jpg/png images somewhere for download to make cross-platform - put on an Amazon s3 server
* Build mosaics with hand-annotated information, include in movies
* Host mp4s on a server for better quality (YouTube downgrades some to 360p)
* Option to make b&w movies using one filter, to reduce flickering
* Add adjustment step to correct images - remove reseau marks, subtract dark current images, stretch histogram (?)


<!-- Later -->
<!-- ---------------------------------------- -->
<!-- - improve stabilization parameters -->
<!-- - (make ariel movie with override centers, aligned composite, mosaic - test crowdsourcing aspects) -->
<!-- - Add `vg segments` command to build movie segments with more editorial control -->
<!-- - Add `vg init positions` to initialize positions.csv, which has angular size of target / camera FOV -->
<!-- - Update `vg centers` to use positions.csv to know when to turn centering on/off - remove centering.csv -->


Version 0.43 (2016-08)
----------------------------------------
- `vg target` can take a targetpath or volume range
- `vg clips` framerate depends on angular size of target and target-specific constant 
- Return `vg center` to previous role - will just append new center information to `centers.csv` for now

Version 0.42 (2016-08-06)
----------------------------------------
- `vg init centers`:
  - uses expected target size to narrow down Hough circle search for more accurate results - uses SPICE positions
  - uses adaptive thresholding before running blob detection - works better than plain thresholding for pointlike targets
  - reduces Hough Canny edge detector threshold if can't detect a circle in case target is dim - helps a lot
  - aligns image to expected target disc - works better than aligning to any prior image
  - if can't find a circle, fall back to the blob bounding box - stabilization can often handle the rest, so partial targets can be stabilized, even limbs
  - optionally draws expected target size on images, based on positions.csv
- `vg test` draws expected target size on centered images, based on positions.csv
- Commands can write output to logfile 'log.txt'

Filled in lots of mis-centered images, but more small stabilization problems than v0.41 - need to align final few pixels

Made another stabilized Voyager 1 Jupiter rotation movie (color)

Version 0.41 (2016-08-02)
----------------------------------------
- Specify composite images with color weights and x,y offsets
- Add `vg init centers <vol>` command - writes stabilized centers to `centers.csv`
- `vg center <vol>` and `vg center <imageId>` now just use `centers.csv` and `centersOverride.csv`
- Add `vg grab` command 
- Changed stabilization routine so it stabilizes against every 10 good frames, instead of against previous frame, as Jupiter tended to drift to the left. Had also tried stabilizing it to first image in sequence, but jittered towards the end. Didn't retest it on Uranus.

Still fairly jittery - noise/gaps cause stabilization to stutter

Made stabilized Voyager 1 Jupiter rotation movie (color)

Version 0.40 (2016-07-28)
----------------------------------------
- Add ECC (Enhanced Correlation Coefficient) stabilization [13] to `vg center` step to align centered images more accurately

Made Uranus system movie (color/bw)

Version 0.37 (2016-07-27)
----------------------------------------
- Update `vg center` to use records in centers.csv, if available
- Option to use jpeg intermediate files to save space and speed development
- Add `vg test` command to test center detection
- Change commands to verbs

Version 0.36 (2016-07-19)
----------------------------------------
- Add `vg retarget` command to print out new retargeting records
- Add `vg adjustments` command to separate adjusting and centering images into separate steps

Made Uranus movies (color)

Version 0.35 (2016-07-19)
----------------------------------------
- Combine clips into single movies (eg for Neptune), then a movie combining all movies

Made Uranus system movie (bw)

Version 0.34 (2016-07-18)
----------------------------------------
- Control movie speed with `db/framerates.csv` file

Version 0.33 (2016-07-17)
----------------------------------------
- Handle wildcards and ranges in commands, eg `vg images 5101-5120`, `vg images 51*`
- Add `vg list` command to show status of volumes
- Add -y option to overwrite existing data for a step
- Retarget rings to the main planet so they're included with the appropriate movie

Made Uranus bw and color flyby movies

Version 0.32 (2016-07-16)
----------------------------------------
- Handle relabelling of multitarget images, eg a file may be labelled Titan but it gets centered on Neptune
- Add titles for each movie segment

Made Triton flyby movie bw

Version 0.31 (2016-07-16)
----------------------------------------
- Improved Triton approach centering - blob detection was focusing on pixel-wide edge discrepancy.
- Handle movie targets like `Neptune/Voyager2/Triton`, or just `//Triton`
- Passing 25/31 (80%) of edge case tests

Version 0.30 (2016-07-15)
----------------------------------------
- Better small/point-like detection with blob detector below 12x12 pixels, before Hough circle detector used
- Use db/centers.csv file to turn off centering at closest approach and slow down movie (currently only Neptune data available)
- Faster movie creation

Made slightly better movies for Neptune flyby, both b&w and color, incl Triton.

Version 0.20 (2016-07-12)
----------------------------------------
- Added command line interface
- Added target discrimination - sorts images and movies into folders based on planet, spacecraft, image target, and camera
- Uses Hough circle detection for centering - still fairly jittery, esp for small circles and crescents
- Uses CALIB images, which have more contrast and darker backgrounds, which helps with circle detection in Neptune images
- Preliminary handling of automatic colorization of frames and movies

Made rough movies for Neptune flyby from volumes 8201-8210, both b&w and color

Version 0.10 (2016-07-04)
----------------------------------------
- No command line interface
- Able to piece together a movie from complete volumes, but no target discrimination
- Uses Blob detection and Hough circle detection for centering
- Uses RAW images, which worked alright for some of the Jupiter images, but not Neptune, which has brighter backgrounds

Made b&w movie for Jupiter approach from volumes 5104-5105


License
----------------------------------------

This software is released under the MIT license - see LICENSE.md.



[1]: http://pds-rings.seti.org/voyager/
[2]: http://www.mmedia.is/bjj/utils/img2png/
[3]: https://www.scipy.org/
[4]: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#cv2.HoughCircles
[5]: http://www.numpy.org/
[6]: http://matplotlib.org/
[7]: https://ffmpeg.org/
[8]: https://python-pillow.org/
[9]: https://www.continuum.io/downloads
[10]: https://pypi.python.org/pypi/tabulate
[11]: https://github.com/AndrewAnnex/SpiceyPy
[12]: http://naif.jpl.nasa.gov/naif/
[13]: https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/
[14]: https://github.com/erikrose/more-itertools
