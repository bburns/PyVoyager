# PyVoyager History

<!-- - Add `vg denoise` step - black out bottom and right 3 pixels, fill in single pixel horizontal lines, black out rectangular blocks -->
<!-- - Add `db/denoising.csv` file to control turning denoising step off for certain images (e.g. moons orbiting Uranus, faint rings) -->
<!-- - Add `brightness.csv` file for `vg adjust` step - override histogram stretching for certain files where noise throws off the brightness adjustment. (first try ignoring 255 values) -->
<!-- - `vg center` in progress -->

Version 0.5 (2016-09-16)
----------------------------------------
- `vg download`, `vg unzip` handle EDR archives
- `vg import` converts EDR IMQ files to ISIS CUB files in reorganized folders, with newer PDS volume organization (e.g. volume 5101)

Version 0.49 (2016-08-07)
----------------------------------------
- Switching to Linux and EDR archives so can use ISIS - `vg download` downloads EDR volumes 1-33 now

Version 0.485 (2016-08-07)
----------------------------------------
- Working on `vg map` - preliminary results working okay - could project Jupiter approach frames into cylindrical map, though without photometric corrections. Decided to switch to using ISIS.

Version 0.48 (2016-08-07)
----------------------------------------
- Add `vg crop` command and `crops.csv` to crop/zoom in on images
- Add `vg pages` command to generate intro, epilogue, credits, etc.

Added crop/zoom images into Voyager 1 Jupiter encounters - Io volcanoes, best moon images, etc.

Version 0.47 (2016-08-22)
----------------------------------------
- `vg movies` can assemble movies from arbitrary segments for more editorial control, e.g. mix wide angle with narrow angle segments

Made Voyager 1 Jupiter encounter movies

Version 0.46 (2016-08-20)
----------------------------------------
- Add `-align` option to `vg composite` - attempts to align channels using feature detection and matching
- Fix `vg adjust` brightness enhancement to ignore hot pixels unless small moon. Improved brightness of dark moon pics and eliminated posterized look from some images due to 16-bit to 8-bit conversion.
- Add `vg clear <step> <vols>` command to remove folders, as -y option sometimes fails due to Windows having a lock on a file, e.g. thumbs.db.

Made Voyager 1 Io encounter movie - cleaned up from prior version

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

