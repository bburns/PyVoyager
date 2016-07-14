
PyVoyager
========================================

PyVoyager automatically creates and stabilizes Voyager flyby movies - the eventual goal is to produce a single movie with titles and audio automatically, with each planet and target having a separate segment.

It's in an early stage of development, but is still usable for downloading and extracting datasets, and assembling rough movies. I'm working on improving the centering/stabilization and coloring routines.

There are a total of 70k+ images in the Voyager archives - the datasets are rather large - 1-3GB per tar volume, with 87 volumes in total, so there is a lot to explore! 


Example Movies
----------------------------------------

These movies are still in early stages, so pardon the jitters and the mini 'volcanoes' (leftover from removal of reseau marks). 

https://www.youtube.com/watch?v=VF3UCo2P-4Y  
Voyager 2 Neptune flyby v0.2 - note Triton orbiting Neptune and the winds on the planet blowing in the opposite direction

https://www.youtube.com/watch?v=c8O2BKqM0Qc  
Voyager 2 Neptune flyby color v0.2 - automatically colorized version

https://www.youtube.com/watch?v=o4zh8C-ma_A  
Voyager 1 Jupiter approach v0.1 - (raw images with reseau marks)


Pipeline
----------------------------------------

Voyager consists of a command line interface to a pipeline of Python programs with the following steps: 

* 1. Download Voyager datasets from **PDS archives** [1] 
* 2. Extract the contents of the tar.gz archives
* 3. Convert Voyager IMG images to PNGs using **img2png** [2]
* 4. Center images on the target using blob detection using **SciPy** [3] and Hough circle detection using **OpenCV** [4]. Other libraries used include **NumPy** [5] and **Matplotlib** [6].
* 5. Colorize frames by combining images, where possible, using **OpenCV**
* 6. [Build mosaics from images, where possible]
* 7. Arrange images into folders corresponding to different planets/spacecrafts/targets/cameras
* 8. Make movies from previous step [and add titles and music] using **ffmpeg** [7]


Installation
----------------------------------------

You'll need **Windows**, **Python 2.7**, **img2png** [2], **OpenCV** [4], **SciPy** [3], **NumPy** [5], **Matplotlib** [6], and **ffmpeg** [7]. 


Compatibility
----------------------------------------

The main limitation is **img2png**, which is only available on Windows - this is what converts the PDS IMG files to PNGs, so it's a crucial step.

In the future, the PNG images could be hosted elsewhere for download, to skip the tarfile and extraction and conversion steps, and allow for cross-platform use. 


Usage
----------------------------------------

Download a tarfile volume, e.g. volume 5101 - the first dataset, Jupiter approach

    > vg download 5101
    
Unzip the tarfile

    > vg unzip 5101

Convert the IMG files to PNGs with **img2png**

    > vg images 5101

Center the images on the main body in the images

    > vg centers 5101

or do all of these steps automatically (performs missing steps)

    > vg centers 5101

Colorize the images

    > vg composites 5101

Then make movies of all the downloaded datasets, organized by planet/spacecraft/target/camera

    > vg movies


How it works
----------------------------------------

The data for each step is put into the following folders in the 'data' subfolder: 

    step1_downloads
    step2_unzips
    step3_images
    step4_centers
    step5_composites
    step6_mosaics
    step7_targets
    step8_movies

There are 87 PDS volumes for all the Voyager images, each ~1-3GB, as described here http://pds-rings.seti.org/voyager/iss/calib_images.html. 

Each image comes in 4 formats - RAW, CLEANED, CALIB, and GEOMED. RAW images are just that, and are 800x800 pixels, and include the reseau marks (the grid of dots) used for calibration. CLEANED images have had the reseau marks removed, but leave noticeable artifacts that look like volcanoes on the limbs of planets. CALIB images have had dark images subtracted from the CLEANED images, and GEOMED are the CALIB images geometrically corrected and projected to 1000x1000 pixels. Ideally the RAW images would be used with a better reseau removal algorithm, but for now the CALIB images are used. 

After downloading the tar files, unzipping them, and extracting the PNGs, the CALIB images are centered based on a Hough circle detection algorithm. This works for most cases, but there is still noticeable jitter and frames where it doesn't work very well, so this has room for improvement.

The volumes come with index files for all the images they contain, which have been compiled into one smaller file using `vg init files`. The resulting file (db/files.csv) looks like this:

    volume,fileid,phase,craft,target,time,instrument,filter,note
    5104,C1541422,Jupiter,Voyager1,Jupiter,1979-02-01T00:37:04,Narrow,Blue,3 COLOR ROTATION MOVIE
    5104,C1541424,Jupiter,Voyager1,Jupiter,1979-02-01T00:38:40,Narrow,Orange,3 COLOR ROTATION MOVIE
    5104,C1541426,Jupiter,Voyager1,Jupiter,1979-02-01T00:40:16,Narrow,Green,3 COLOR ROTATION MOVIE
    ...

though different targets and camera records can be also interleaved with others.

This list of files has been compiled into a list of composite frames to build using the `vg init composites` command, based on repeating groups of filters for the different targets and cameras. The resulting file (db/composites.csv) looks like this: 

    volume,compositeId,centerId,filter
    5104,C1541422,C1541422,Blue
    5104,C1541422,C1541424,Orange
    5104,C1541422,C1541426,Green

This file is used by the `vg composites <volume>` command to generate the color frames. 

The movies are generated with the `vg movies <targets>` command, which links all the images (either B&W or composites, currently set in code) into target subfolders (arranged by planet/spacecraft/target/camera), renumbering them sequentially, and running **ffmpeg** to generate an mp4 movie in each folder. 

That's about it!


Next steps
----------------------------------------

* Improve stabilization/centering routines - use blob detection for small circles (and crescents?), Hough otherwise
* Improve color frame detection and rendering routines - could borrow missing channels from previous frames, use all available channels, use more precise colors than just rgb, eg orange, other ideas? 
* Detect full-frame views and don't try to center them - might need to provide manual annotation for this, or base it on closest approach times
* Slow down the movie at closest approach - base on closest approach times
* Add titles to each target movie
* Combine movie segments into single movie, adding audio
* Option to make b&w movies using one filter, to reduce flickering
* Build mosaics with hand-annotated information, include in movies
* Split centering step into two phases - detect center and offset, and apply offset to possibly different image type
* Add adjustment step to correct images - remove reseau marks, subtract dark current images, optimize contrast(?)
* Handle wildcards and ranges, eg `vg images 5101-5120`, `vg images 51*`
* Host PNG images somewhere for download


Version 0.3
----------------------------------------
- Include default centering information in centers<volume>.csv files


Version 0.2 (2016-07-12)
----------------------------------------
- Added command line interface
- Added target discrimination - sorts images and movies into folders based on planet, spacecraft, image target, and camera
- Uses Hough circle detection for centering - still fairly jittery, esp for small circles and crescents
- Uses CALIB images, which have more contrast and darker backgrounds, which helps with circle detection in Neptune images
- Preliminary handling of automatic colorization of frames and movies

Made rough movies for Neptune flyby from volumes 8201-8210, both b&w and color.


Version 0.1 (2016-07-04)
----------------------------------------
- No command line interface
- Able to piece together a movie from complete volumes, but no target discrimination
- Uses Blob detection and Hough circle detection for centering
- Uses RAW images, which worked alright for some of the Jupiter images, but not Neptune, which has brighter backgrounds

Made b&w movie for Jupiter approach from volumes 5104-5105. 


[1]: http://pds-rings.seti.org/archives/
[2]: http://www.mmedia.is/bjj/utils/img2png/
[3]: https://www.scipy.org/
[4]: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#cv2.HoughCircles
[5]: http://www.numpy.org/
[6]: http://matplotlib.org/
[7]: https://ffmpeg.org/

