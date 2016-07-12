
Voyager
========================================

Creates and stabilizes Voyager flyby movies. 

Voyager consists of a pipeline of Python programs with the following steps: 

* 1. Download Voyager datasets from **PDS archives** [1] 
* 2. Extract the contents of the tar.gz archives
* 3. Convert Voyager IMG images to PNGs using **img2png** by Bjorn Jonsson [2]
* 4. Center images on the target using blob detection using **SciPy** [3] and Hough circle detection using **OpenCV** [4]. Other libraries used include **NumPy** [5] and **Matplotlib** [6].
* 5. Colorize frames by combining images, where appropriate
* 6. Build mosaics from images, where appropriate
* 7. Arrange images into folders corresponding to different planets/spacecrafts/targets/cameras
* 8. Make movies from previous step and add titles and music using **ffmpeg** [7]

To center the images, blob detection is first done to identify the largest contiguous region in the image, then if this region is not approximately square, circle detection is done in order to identify the center and radius of the planet/moon. 

The current version is likely to undergo changes in order to handle different targets and cameras used, and to improve the centering algorithm for large planet images. 


Usage
----------------------------------------

Download a tarfile volume, e.g. volume 5101 - the first dataset, Jupiter approach

    > vg download 5101
    
Unzip the tarfile

    > vg unzip 5101

Convert the PDS IMG files to PNGs

    > vg images 5101

Calculate the centers of the main body in the images

    > vg calc centers 5101

Center the images

    > vg centers 5101

or to do all of these steps, 

    > vg centers 5101

Then make movies of all the downloaded datasets, organized by planet/spacecraft/target/camera

    > vg movies



Version 0.2
----------------------------------------
- Add command line interface
- Working on automatic colorization of movies
2016-07-07


Version 0.1
----------------------------------------
The sequence from VGISS_5104-5105 works best at the moment, so those were combined into one movie. 
2016-07-04


Next steps
----------------------------------------

* Handle larger planet images - not centering correctly, eg in VGISS_5106.
* Option to make movie using one filter, to reduce flickering. 


[1]: http://pds-rings.seti.org/archives/
[2]: http://www.mmedia.is/bjj/utils/img2png/
[3]: https://www.scipy.org/
[4]: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#cv2.HoughCircles
[5]: http://www.numpy.org/
[6]: http://matplotlib.org/
[7]: https://ffmpeg.org/

