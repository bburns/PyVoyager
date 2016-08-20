
PyVoyager
========================================

Version 0.46 inprogress

PyVoyager automatically creates and stabilizes Voyager flyby movies - the eventual goal is to produce a single movie with titles and audio as automatically as possible, with each planet and target having a separate segment. 

The most challenging part will be reconstructing the geometry and assembling the mosaics automatically, as the camera pointing information available is not very accurate. 

This is a large project, so it's designed to be split up among different people working on different segments, coordinated through .csv files. 

It's in an early stage of development, but is still usable for downloading and extracting datasets, and assembling rough movies. 

There are a total of 70k+ images in the Voyager archives - the datasets are rather large - 1-3GB per compressed volume, with 87 volumes in total, so there is a lot to explore!

You can read more about the Planetary Data System (PDS) which hosts the archives here - http://www.planetary.org/explore/space-topics/space-imaging/data.html.


Example Movies
----------------------------------------

These movies are still in early stages, so pardon the jitters and the mini 'volcanoes' (leftover from removal of reseau marks).

http://imgur.com/LO7Dnww  
Voyager 2 Io approach v0.43

https://www.youtube.com/watch?v=i38gzr6j5q4  
Rough draft of Voyager 1 flyby of Jupiter system (13mins) v0.45

https://www.youtube.com/watch?v=_YT4XINDxjk  
Voyager 2 Uranus system flyby in color and black and white v0.43

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


Issues
----------------------------------------

There's a Trello board to track issues and progress here - https://trello.com/b/kEkGDMYR/voyager


<!-- Denoising Images -->
<!-- ---------------------------------------- -->

<!-- The images are denoised using ___ -->


Centering Images
----------------------------------------

Images where the target fits completely in the frame are centered using blob detection [17], Hough circle detection [16], and ECC Maximization [15]. The expected target radius is calculated through SPICE data [12], from which the spacecraft and target position can be determined - this is used to help limit the Hough circle search, and then to draw a disc with the expected target size to which the image is aligned using ECC Maximization. The Hough circle detection is only accurate to a few pixels, so the ECC Maximization is needed for the final stabilization. 

Here are a couple of images showing the result of the centering/stabilization - the yellow circle is the expected target size:

<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1532335_centered_Orange.jpg" width="400">
<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1524138_centered_Blue.jpg" width="400">

Centering is turned off at closest approach by determining when the target size is over a threshold (e.g. when the diameter is over 80% of the image width). 


Aligning Composites
----------------------------------------

Composite channels for closeup images are aligned using feature detection [18] and matching, with RANSAC [19] to eliminate outliers from a least-squares fit model for the translation (which amounts to the translation tx, ty between images being an average of the feature movements).

In more detail, 'interesting' features are detected using ORB [20] in one image, and matched with their corresponding point in another image. This is done for dozens-hundreds of interest points - they are each described with a feature vector, also obtained by ORB, then matched up with their corresponding point by a brute-force search. The RANSAC algorithm is used to throw out outliers, which would otherwise throw off the determined average translation. 

If this approach fails to find a good translation (due to lack of enough corresponding points, for instance), it will fall back on ECC Maximization [15] to try to align the images. 

Here is an image showing what the feature-matching process looks like, and the resulting combined image (with enhanced contrast). 

<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1637948_matching.jpg" width="800">
<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1637948_aligned.jpg" width="400">


<!-- What you can do -->
<!-- ---------------------------------------- -->

<!-- Although the goal is to complete the movies in as automated fashion as possible, there are still places where manual intervention is required -  -->

<!-- - Some frames don't get centered correctly due to noise, or being on the edge of an image, etc., so they need to be manually centered by editing the `db/centersOverride.csv` file, or (eventually) using the `vg center <imageId> <x offset>, <y offset>` command. -->
<!-- - Centering needs to be manually turned off at close approach and back on again at departure - this is done in `db/centering.csv`.  -->
<!-- - Multi-target images often need to be relabelled to the largest target in the image (or whatever the centering routines center on) - this is done in the `db/retargeting.csv` file. -->
<!-- - Close-up composite images need to be manually aligned - e.g. the closeups of the clouds of Jupiter, by editing the `db/composites.csv` file. The weight of the different filters can also be adjusted there.  -->
<!-- - Movie frame rates need to be adjusted so interesting images stay on the screen longer - this is done in the `db/framerates.csv` file.  -->
<!-- - And eventually, mosaics would need to be specified manually in a `db/mosaics.csv` file.  -->


Pipeline
----------------------------------------

Voyager consists of a command line interface to a pipeline of Python programs with the following steps (many not completed yet):

* Download - download archives from **PDS archives** [1]
* Unzip - decompress archive volumes
* Convert - convert RAW images to pngs using **img2png** [2]
* Flatfield - subtract good flatfields
* Denoise - identify/eliminate noise where possible
* Adjust - rotate180, histogram stretch
* Center - center and stabilize images
* Dereseau - remove reseau marks cleanly
* Inpaint - fill in black/white areas with pixels from prior frame
* Undistort - geometric correction 800x800->1000x1000
* Composite - combine channels using auto+manual info
* Mosaic - combine images using auto+manual info
* Colorize - colorize bw images with lores color info - need to know viewing geometry, so after mosaic step
* Crop - crop and zoom frames, eg io volcano
* Annotate - add caption information, point out features, etc
* Clips - combine images into short movies, one per target
* Movies - combine clips into movies, add music


Installation
----------------------------------------

You'll need **Windows**, **Python 2.7**, **img2png** [2], **OpenCV** version 3 [4], **SciPy** [3], **NumPy** [5], **Matplotlib** [6], **Pillow** [8], **tabulate** [10], **more-itertools** [14], and **ffmpeg** [7]. Building one of the included .csv data files (positions.csv) requires **SpiceyPy** [11], a Python interface to **SPICE** [12]. 

I started with an installation of **Anaconda** [9], a Python distribution with lots of pre-installed scientific libraries, including **Matplotlib**, **NumPy**, **Pillow**, and **SciPy**, and added the rest with `pip`. 

At this point I'm not sure how rough the installation process might be. 

Note that **img2png** is only available on Windows - in the future, the PNG images (or JPGs) could be hosted elsewhere for download, to skip the tarfile and extraction and conversion steps, and allow for cross-platform use, if the editing needs to be distributed.


Usage
----------------------------------------

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

Convert the IMG files to PNGs with **img2png**

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


Parameters
----------------------------------------

All configuration settings are stored in `config.py` - the goal is for the same set of parameters to work across all datasets as much as possible.


More details
----------------------------------------

The data for each step is put into the following folders in the `data` subfolder:

    step01_downloads
    step02_unzips
    step03_images
    step04_adjustments
    step05_denoised
    step06_centers
    step07_composites
    step08_mosaics
    step09_annotations
    step10_targets
    step11_titles
    step12_clips
    step13_movies

There are 87 PDS volumes for all the Voyager images, each ~1-3GB, as described here http://pds-rings.seti.org/voyager/iss/calib_images.html.

Each image comes in 4 formats - RAW, CLEANED, CALIB, and GEOMED.

- RAW images are the least processed images available - they're 800x800 pixels, and include the reseau marks (the grid of dots) used for calibration.
- CLEANED images have had the reseau marks removed, but leave noticeable artifacts that look like volcanoes on the limbs of planets.
- CALIB images have had dark images subtracted from the CLEANED images, and
- GEOMED are the CALIB images geometrically corrected and projected to 1000x1000 pixels.

Ideally the RAW images would be used with a better reseau removal algorithm, but for now the CALIB images are used.

After downloading the tar.gz files, unzipping them, extracting the PNGs, adjusting and denoising them, the CALIB images are centered based on blob detection, Hough circle detection, the expected target radius, and ECC maximization [3] for stabilization. See the section on centering below for more details. 

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

The clips are generated with the `vg clips [targetpath]` command, which links all the images into target subfolders (arranged by planet/spacecraft/target/camera), numbering them sequentially, and running **ffmpeg** to generate an mp4 clip for each. The target size is also used to control the speed of the movie, slowing down when the target is closer, but the framerate can also be controlled via the `framerateConstants.csv` and `framerates.csv` files. 

The `vg movies` command then concatenates all available clips into movies, using the order specified in `db/movies.csv`. 


Testing
----------------------------------------

Some centering test images are included in the `test/center` folder, and their correct center values in `test/testCenterFiles.csv`. You can run the tests on them with `vg test center`. The goal is to include some easy targets and lots of edge cases to test the centering/stabilizing routines.

Denoising test images are located in `test/denoise` - you can run the tests with `vg test denoise` - check the results in the same denoise folder.


History
----------------------------------------

<!-- - Add `vg denoise` step - black out bottom and right 3 pixels, fill in single pixel horizontal lines, black out rectangular blocks -->
<!-- - Add `db/denoising.csv` file to control turning denoising step off for certain images (e.g. moons orbiting Uranus, faint rings) -->
<!-- - Add `brightness.csv` file for `vg adjust` step - override histogram stretching for certain files where noise throws off the brightness adjustment. (first try ignoring 255 values) -->

Version 0.46 (2016-08-)
----------------------------------------
- Add `-align` option to `vg composite` - attempts to align channels using feature detection and matching
- Fix `vg adjust` brightness enhancement to ignore hot pixels unless small moon. Improved brightness of dark moon pics and eliminated posterized look from some images due to 16-bit to 8-bit conversion. 
- Add `vg clear <step> <vols>` command to remove folders, as -y option sometimes fails due to Windows having a lock on a file, e.g. thumbs.db. 

Version 0.45 (2016-08-14)
----------------------------------------
- Add `vg inpaint` step to fill in missing or whited out parts of target, where possible
- Frame rate constants can be set by System-Craft-Target-Camera
- Add `vg test composite` to test compositing routines, with several examples for validation

Made Voyager 1 Jupiter system movie - lots of edits to composites.csv and framerates.csv

Jupiter rotation segment still a bit unstable - cloud and moon composites not aligned, except where centered.

Version 0.44 (2016-08-12)
----------------------------------------
- Add optional `vg annotate` step - annotate images with imageId, date/time, distance (km), NOTE field text
- `vg clips` can include additional images after frames, as specified in `additions.csv` - use to add hand-tuned mosaics, etc
- `vg adjust` ignores brightest n pixels before doing histogram stretch, to avoid hotspots keeping image dim
- Remove `vg clip` bw/color options - all clips will draw from composite step, which will include single channel 'composites' - keeps pipeline simple

Version 0.43 (2016-08-08)
----------------------------------------
- `vg center`:
  - return to previous role - will append new center information to `centers.csv` for now
  - don't try to center image if target size is larger than some threshold (replaces existing `centering.csv` file)
  - don't center image if includes 'search' in NOTE field - avoids centering ring/satellite searches
  - use new `centering.csv` file to turn centering on/off for specific images - overrides above settings
  - use `framerates.csv` to change frame rates per image - can use sticky ID to set it for a target until it's changed
- `vg clips` framerate depends on angular size of target and target-specific constant, set in `targets.csv`
- `vg target` can take a targetpath or volume range

Jupiter rotation movie is still a bit unstable - needs another pass. But Uranus looks fairly good. 

Made Io approach clip, Uranus system movie. 

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
[15]: http://xanthippi.ceid.upatras.gr/people/evangelidis/ecc/
[16]: https://en.wikipedia.org/wiki/Circle_Hough_Transform
[17]: https://en.wikipedia.org/wiki/Blob_detection
[18]: https://en.wikipedia.org/wiki/Feature_detection_(computer_vision)
[19]: https://en.wikipedia.org/wiki/RANSAC
[20]: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_orb/py_orb.html
