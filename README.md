
PyVoyager
========================================

Creates and stabilizes Voyager flyby movies. 

PyVoyager consists of a pipeline of Python programs with the following steps: 

* 0. Download Voyager datasets from **PDS archives** [1] 
* 1. Extract the contents of the tar.gz archives
* 2. Convert Voyager PDS images to PNGs using **img2png** by Bjorn Jonsson [2]
* 3. Center images on the target using blob detection using **SciPy** [3] and Hough circle detection using **OpenCV** [4]. Other libraries used include **NumPy** [5] and **Matplotlib** [6].
* 4. Make a movie from the images from each volume using **ffmpeg** [7]
* 5. Combine the separate movies into one movie with **ffmpeg**
* 6. (Add music with **ffmpeg**)

To center the images, blob detection is first done to identify the largest contiguous region in the image, then if this region is not approximately square, circle detection is done in order to identify the center and radius of the planet/moon. 

The current version is likely to undergo changes in order to handle different targets and cameras used, and to improve the centering algorithm for large planet images. 


Version 0.1 
----------------------------------------

The sequence from VGISS_5104-5105 works best at the moment, so those were combined into one movie. 

2016-07-04


Next steps
----------------------------------------

* Handle larger planet images - not centering correctly, eg in VGISS_5106.
* Option to make movie using one filter, to reduce flickering. 
* Put images into separate folders for each target sequence, eg JupiterTelescope, JupiterWide, Europa, Io. Each can make a movie with a different framerate. 
* Add command-line interface, e.g. something like vg download 5105-5106, vg unzip 5105, vg pngs 5110, vg center 5118, vg all 5119.



[1]: http://pds-rings.seti.org/archives/
[2]: http://www.mmedia.is/bjj/utils/img2png/
[3]: https://www.scipy.org/
[4]: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#cv2.HoughCircles
[5]: http://www.numpy.org/
[6]: http://matplotlib.org/
[7]: https://ffmpeg.org/

