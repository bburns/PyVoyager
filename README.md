# PyVoyager

PyVoyager automatically creates and stabilizes Voyager flyby movies - the eventual goal is to produce a single movie with titles and audio as automatically as possible, with each planet and target having a separate segment. 

- [PyVoyager](#pyvoyager)
  - [About](#about)
  - [Example Movies](#example-movies)
  - [Issues](#issues)
  - [Contributing](#contributing)
  - [Pipeline](#pipeline)
  - [Sources](#sources)
  - [Technical](#technical)
  - [History](#history)
  - [License](#license)
  
## About

Voyager 1 and 2 sent back over 70,000 images, so there is a lot to explore! 

Unfortunately the cameras were not able to point very accurately at their targets, resulting in jittery image sequences. PyVoyager centers the target planet or moon in the frame, and creates movies from the image sequences.

<!-- Before:  -->
<!-- After: -->

Example Movies
----------------------------------------

<!-- Here is an example raw image sequence -  -->

<!-- and here it is, centered -  -->


Here is Voyager 2's flyby of Io - any mini 'volcanoes' are actually leftover from the removal of reseau marks (a grid of black dots) -

https://www.youtube.com/watch?v=lYUgU-Bc1_w  
Voyager 1 Jupiter flyby, mostly false color (3mins) v0.47

http://imgur.com/LO7Dnww  

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


## Contributing

Images where the target fits completely in the frame are centered using blob detection [17], Hough circle detection [16], and ECC Maximization [15]. The expected target radius is calculated through SPICE data [12], from which the spacecraft and target position can be determined - this is used to help limit the Hough circle search, and then to draw a disc with the expected target size to which the image is aligned using ECC Maximization. The Hough circle detection is only accurate to a few pixels, so the ECC Maximization is needed for the final stabilization. 

I'm in the process of moving the system from Windows to Linux so it can use [ISIS][isis], which also requires switching from PDS archives to EDR archives - some of the README documentation is still geared towards the older system - the new one is in transition. 

<!-- ## What you can do -->

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
* Crop - crop and zoom frames, eg io volcanoes
* Annotate - add caption information, point out features, etc
* Clips - combine images into short movies, one per target
* Movies - combine clips into movies, add music


## Sources

You can read more about the Planetary Data System (PDS) which hosts the archives [here][pds].


## Technical

For more details, including how to run the program, see [TECHNICAL.md](TECHNICAL.md).


## History

For the program and movie version history see [HISTORY.md](HISTORY.md).


License
----------------------------------------

This software is released under the MIT license - see LICENSE.md.

[pds]: https://pds.nasa.gov/
[playlist]: https://www.youtube.com/playlist?list=PLxP4UgQGtMiLvyKjT7BQ-ht905VvNSaFP
[trello]: https://trello.com/b/kEkGDMYR/voyager
[isis]: https://isis.astrogeology.usgs.gov/
