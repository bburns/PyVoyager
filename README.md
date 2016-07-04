
PyVoyager
========================================

Stabilization of Voyager flyby movies. 

PyVoyager consists of a pipeline of Python programs with the following steps: 

* 0. Download Voyager datasets from __ 
* 1. Extract the contents of the tar.gz archives
* 2. Convert Voyager images to PNGs using __ from __
* 3. Center images on the target using blob and Hough circle detection
* 4. Make a movie from the images from each volume using ffmpeg
* 5. Combine the separate movies into one movie with ffmpeg


Version 0.1 
----------------------------------------

2016-07-04



Next
----------------------------------------
* Handle larger planet images - not centering correctly, eg in 5106
* Dump images into separate folders for each target sequence, eg JupiterTelescope, JupiterWide, Europa, Io. Each makes a movie with a different framerate. Dump all movies together with titles, add music. 


