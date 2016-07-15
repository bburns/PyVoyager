
PyVoyager
========================================

PyVoyager automatically creates and stabilizes Voyager flyby movies - the eventual goal is to produce a single movie with titles and audio automatically, with each planet and target having a separate segment.

It's in an early stage of development, but is still usable for downloading and extracting datasets, and assembling rough movies. I'm working on improving the centering/stabilization and coloring routines.

There are a total of 70k+ images in the Voyager archives - the datasets are rather large - 1-3GB per tar volume, with 87 volumes in total, so there is a lot to explore. 


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
* 4. Center images on the target using blob detection using **SciPy** [3] and Hough circle detection using **OpenCV** [4]. Other libraries used include **NumPy** [5] and **Matplotlib** [6]
* 5. Colorize frames by combining images, where possible, using **OpenCV**
* 6. [Build mosaics from images with hand-annotated information - lots of work though]
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

Then make b&w or color movies of all the downloaded datasets, organized by planet/spacecraft/target/camera

    > vg movies bw|color


Parameters
----------------------------------------

All configuration settings are stored in `config.py` - if you run into problems with centering there are some parameters there which you can tweak, notably `blobThreshold`, `blobAreaCutoff`, and `cannyUpperThreshold`. Otherwise you can try modifying the centering algorithm in `vgBuildCenters.py` and `libimg.py`.

The goal is for the same set of parameters to work across all datasets and avoid the need for more specification files, though not sure how possible that will be at this point. 


Testing
----------------------------------------

Some test images are included in the `test/images` folder, and their correct bounding box values, where known, in `test/testfiles.csv`. You can run the tests on them with `cd test` and `python testCentering.py`. The goal is to include some easy targets and lots of edge cases to test the centering routines. If you find a frame that doesn't center correctly you can throw the original into the images folder and add a record to testfiles.csv.


How it works
----------------------------------------

The data for each step is put into the following folders in the `data` subfolder: 

    step1_downloads
    step2_unzips
    step3_images
    step4_centers
    step5_composites
    step6_mosaics
    step7_targets
    step8_movies

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

The small/point-like targets are handled fairly well by the blob detection routine. Where the area is larger than some small value though, eg 12x12 pixels, the detection is better handled by the Hough circle detector, which works well on the 'normal' targets and targets with gaps.

But the Hough detector doesn't handle targets with centers outside of the image, as it assumes otherwise, and it also doesn't work too well with crescents, as they are basically two partial circles, so there can be some jitters in the movies. Those two cases are not well-accounted for at the moment. 

Targets larger than the field of view must be handled specially, as the blob and Hough detectors will pick up spurious features to center on. So a file `db/centering.csv` is set up to tell the centering routine when to turn centering off then back on after closest approach, based on the image name. This must be set up manually, and looks like this - 

    planetCraftTargetCamera,centeringOff,centeringOn
    NeptuneVoyager2NeptuneNarrow,C1127459,C1152407
    NeptuneVoyager2NeptuneWide,C1137509,C1140815
    NeptuneVoyager2TritonNarrow,C1139255,C1140614

This table is also used to tell the movie creation step to slow down the frames at closest approach. The alternative would be to base these steps more automatically on distance from the planet and angular radius, but that might be a future enhancement - it would also allow for more gradual slow-down and speed up around closest approach. 

The PDS volumes come with index files for all the images they contain, which have been compiled into one smaller file using `vg init files`. The resulting file (`db/files.csv`) looks like this:

    volume,fileid,phase,craft,target,time,instrument,filter,note
    5104,C1541422,Jupiter,Voyager1,Jupiter,1979-02-01T00:37:04,Narrow,Blue,3 COLOR ROTATION MOVIE
    5104,C1541424,Jupiter,Voyager1,Jupiter,1979-02-01T00:38:40,Narrow,Orange,3 COLOR ROTATION MOVIE
    5104,C1541426,Jupiter,Voyager1,Jupiter,1979-02-01T00:40:16,Narrow,Green,3 COLOR ROTATION MOVIE
    ...

though different targets and camera records can be also interleaved with others.

This list of files has been compiled into a list of composite frames to build using the `vg init composites` command, based on repeating groups of filters for the different targets and cameras. The resulting file (`db/composites.csv`) looks like this: 

    volume,compositeId,centerId,filter
    5104,C1541422,C1541422,Blue
    5104,C1541422,C1541424,Orange
    5104,C1541422,C1541426,Green

This file is used by the `vg composites <volume>` command to generate the color frames. 

The movies are generated with the `vg movies bw|color` command, which links all the images into target subfolders (arranged by planet/spacecraft/target/camera), renumbering them sequentially, and running **ffmpeg** to generate an mp4 movie in each folder. 

That's about it!


Next steps
----------------------------------------

* Add titles to each target movie
* Handle wildcards and ranges, eg `vg images 5101-5120`, `vg images 51*`
* Improve stabilization/centering routines - handle off-screen centers and crescents
* Improve color frame detection and rendering routines - could borrow missing channels from previous frames, use all available channels, use more precise colors than just rgb, eg orange
* Combine movie segments into single movie, adding audio
* Build mosaics with hand-annotated information, include in movies
* Host PNG images somewhere for download to make cross-platform - put on an Amazon s3 server
* Add adjustment step to correct images - remove reseau marks, subtract dark current images, optimize contrast(?)
* Option to make b&w movies using one filter, to reduce flickering


Version 0.3
----------------------------------------
- Better small/point-like detection with blob detector below 12x12 pixels, before Hough circle detector used
- Use db/centers.csv file to turn off centering at closest approach and slow down movie (currently only Neptune data available)
- Fix bug in `vg init composites` command which threw some color frames off

Made incrementally better movies for Neptune flyby, both b&w and color. 


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

