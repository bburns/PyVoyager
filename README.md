
PyVoyager
========================================

PyVoyager automatically creates and stabilizes Voyager flyby movies. 

It's in an early stage of development, but is still usable for downloading and extracting datasets, and assembling rough movies. I'm working on improving the centering/stabilization and coloring routines.


Examples
----------------------------------------

These are still in early stages, so pardon the jitters and the mini 'volcanoes'. 

https://www.youtube.com/watch?v=VF3UCo2P-4Y  
Voyager 2 Neptune flyby (narrow angle camera) - note Triton orbiting Neptune and the winds on the planet blowing in the opposite direction

https://www.youtube.com/watch?v=c8O2BKqM0Qc  
Voyager 2 Neptune flyby - automatically colorized version

https://www.youtube.com/watch?v=o4zh8C-ma_A  
Voyager 1 Jupiter approach (raw images with riseau marks)


Pipeline
----------------------------------------

Voyager consists of a pipeline of Python programs with the following steps: 

* 1. Download Voyager datasets from **PDS archives** [1] 
* 2. Extract the contents of the tar.gz archives
* 3. Convert Voyager IMG images to PNGs using **img2png** by Bjorn Jonsson [2]
* 4. Center images on the target using blob detection using **SciPy** [3] and Hough circle detection using **OpenCV** [4]. Other libraries used include **NumPy** [5] and **Matplotlib** [6].
* 5. Colorize frames by combining images, where possible
* 6. [Build mosaics from images, where possible]
* 7. Arrange images into folders corresponding to different planets/spacecrafts/targets/cameras
* 8. Make movies from previous step [and add titles and music] using **ffmpeg** [7]


Installation
----------------------------------------




Usage
----------------------------------------

Download a tarfile volume, e.g. volume 5101 - the first dataset, Jupiter approach

    > vg download 5101
    
Unzip the tarfile

    > vg unzip 5101

Convert the IMG files to PNGs

    > vg images 5101

Center the images on the main body in the images

    > vg centers 5101

or do all of these steps automatically

    > vg centers 5101

Colorize the images

    > vg composites 5101

Then make movies of all the downloaded datasets, organized by planet/spacecraft/target/camera

    > vg movies


Compatibility
----------------------------------------

PyVoyager was written on Windows - it's mostly Python code so it could possibly be ported to Linux, except for the **img2png** program, which is only available on Windows at the moment. 


Next steps
----------------------------------------

* Improve stabilization/centering routines
* Improve color frame detection and rendering routines
* Detect full-frame views and don't try to center them - might need to provide manual annotation for this, or base it on closest approach times
* Slow down the movie at closest approach
* Add titles to each target movie
* Option to make b&w movies using one filter, to reduce flickering


Version 0.2 (2016-07-12)
----------------------------------------
- Added command line interface
- Added target discrimination - sorts images and movies into folders based on planet, spacecraft, image target, and camera
- Uses Hough circle detection for centering
- Preliminary handling of automatic colorization of frames and movies

Made movies for Neptune flyby from volumes 8201-8210. 


Version 0.1 (2016-07-04)
----------------------------------------
- No command line interface
- Able to piece together a movie from complete volumes, but no target discrimination
- Uses Blob detection and Hough circle detection for centering

Made movie for Jupiter approach from volumes 5104-5105. 


[1]: http://pds-rings.seti.org/archives/
[2]: http://www.mmedia.is/bjj/utils/img2png/
[3]: https://www.scipy.org/
[4]: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#cv2.HoughCircles
[5]: http://www.numpy.org/
[6]: http://matplotlib.org/
[7]: https://ffmpeg.org/

