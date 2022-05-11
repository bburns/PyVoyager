This document explains how to use PyVoyager.

- [Pipeline](#pipeline)
- [Images](#images)
- [Processing](#processing)
- [File Index](#file-index)
- [Multiple Targets](#multiple-targets)
- [Composites](#composites)
- [Clips](#clips)
- [Movies](#movies)
- [Testing](#testing)

## Pipeline

Voyager consists of a command line interface to a pipeline of Python programs with the following steps (some in progress, marked with [wip] or [future]):

* Download - download archives from [PDS EDR (raw) archives][1]
* Unzip - decompress archive volumes to IMQ files
* Convert - convert RAW images to pngs using [img2png][img2png]
* Import - import IMQ files to ISIS cube files, attach SPICE geometry data with `spiceinit` [future]
* Adjust - rotate 180 degrees, calibrate images
* Flatfield - subtract good flatfields (dark images) [future]
* Dereseau - remove reseau marks cleanly (set to null) [future]
* Denoise - identify/eliminate noise where possible (set to null)
* Undistort - geometric correction using reseau marks 800x800->1000x1000 [future]
* Center - center and stabilize images where entire target is visible
* Inpaint - fill in missing information with pixels from prior frame or average of surrounding pixels - be careful with reseau marks on limbs of target
* Map - project image to cylindrical map using SPICE information, fit there with ISIS jigsaw to refine pointing information [future]
* Colorize - colorize images by pulling missing channels from the map [future]
* Composite - combine channels
* Mosaic - combine images using auto+manual info [future]
* Crop - crop and zoom frames, e.g. volcanoes on Io
* Annotate - add caption information, point out features, etc.
* Target - copy images into target subfolders
* Clips - combine images into short movies, one per target
* Movies - combine images and clips into movies, add music


## Images

There are 87 PDS volumes for all the Voyager images, each ~1-3GB, as described [here](http://pds-rings.seti.org/voyager/iss/calib_images.html).

Each image comes in 4 formats - RAW, CLEANED, CALIB, and GEOMED.

- RAW images are the least processed images available - they're 800x800 pixels, and include the reseau marks (the grid of dots) used for calibration.
- CLEANED images have had the reseau marks removed, but leave noticeable artifacts that look like volcanoes on the limbs of planets.
- CALIB images have had dark images subtracted from the CLEANED images, and
- GEOMED are the CALIB images geometrically corrected and projected to 1000x1000 pixels.

Ideally the RAW images would be used with a better reseau removal algorithm, but for now the CALIB images are used.


## Processing

After downloading the tar.gz files, unzipping them, extracting the CALIB images to PNGs, adjusting and denoising them, the images are centered based on blob detection, Hough circle detection, the expected target radius, and [ECC maximization][ecc] for stabilization. See the section on centering below for more details. 

The expected radius of the target is determined in advance by the `vg init positions` command, which uses SPICE position data, target position, target size, and camera FOV to determine size of target in image, which is stored in `db/positions.csv` (included in the distribution). This helps with the Hough circle detection, and also to stabilize the image. 

## File Index

The PDS volumes come with index files for all the images they contain, which have been compiled into one smaller file using `vg init files`. The resulting file (`db/files.csv`, included in the repo) looks like this:

    fileid,volume,phase,craft,target,time,instrument,filter,note
    C1541422,5104,Jupiter,Voyager1,Jupiter,1979-02-01T00:37:04,Narrow,Blue,3 COLOR ROTATION MOVIE
    C1541424,5104,Jupiter,Voyager1,Jupiter,1979-02-01T00:38:40,Narrow,Orange,3 COLOR ROTATION MOVIE
    C1541426,5104,Jupiter,Voyager1,Jupiter,1979-02-01T00:40:16,Narrow,Green,3 COLOR ROTATION MOVIE
    ...

though different targets and camera records can be also interleaved with others.

## Multiple Targets

One issue is that some images have more than one target in them (e.g. Jupiter with Io) - in the PDS index these images are listed with just one target. For now, you can change which target the image gets sorted under by editing the `db/targets.csv` file (included in the repo) - in the future it could be enhanced to also split the image into two records so each target can be included in the appropriate movie. One retargeting that is performed in advance is from rings to their planet - otherwise the rings would show up in separate movies.


## Composites

The master list of files (`db/files.csv`) has been compiled into a list of composite frames to build using the `vg init composites` command, based on repeating groups of filters for the different targets and cameras. The resulting file (`db/composites.csv`, included in the repo) looks like this:

    compositeId,centerId,volume,filter
    C1541422,C1541422,5104,Blue
    C1541422,C1541424,5104,Orange
    C1541422,C1541426,5104,Green

Note that the compositeId is the id of the first frame in the set. 

The `db/composites.csv` file is then used by the `vg composite <volume>` command to generate the color frames.

For more details on the algorithm used to group images into composite frames, see the comments and code in [vgInitComposites.py](src/vgInitComposites.py).


## Clips

The clips are generated with the `vg clips [targetpath]` command, which links all the images into target subfolders (arranged by planet/spacecraft/target/camera), numbering them sequentially, and running [ffmpeg][ffmpeg] to generate an mp4 clip for each. The target size is also used to control the speed of the movie, slowing down when the target is closer, but the framerate can also be controlled via the `framerateConstants.csv` and `framerates.csv` files. 


## Movies

The `vg movies` command then concatenates all available clips into movies, using the order specified in `db/movies.csv`. 


## Testing

Some centering test images are included in the `test/center` folder, and their correct center values in `test/testCenterFiles.csv`. You can run the tests on them with `vg test center`. The goal is to include some easy targets and lots of edge cases to test the centering/stabilizing routines.

Denoising test images are located in `test/denoise` - you can run the tests with `vg test denoise` - check the results in the same denoise folder.



