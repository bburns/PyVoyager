# Technical

- [Technical](#technical)
  - [Centering Images](#centering-images)
  - [Aligning Composites](#aligning-composites)
  - [Pipeline](#pipeline)
  - [Installation](#installation)
    - [For Windows, set up a Linux virtual machine](#for-windows-set-up-a-linux-virtual-machine)
    - [Starting from Ubuntu 16.04](#starting-from-ubuntu-1604)
  - [Usage](#usage)
  - [Parameters](#parameters)
  - [More details](#more-details)
  - [Testing](#testing)

## Centering Images

Images where the target fits completely in the frame are centered using [blob detection][17], [Hough circle detection][16], and [ECC Maximization][ecc]. The expected target radius is calculated through [SPICE data][12], from which the spacecraft and target position can be determined - this is used to help limit the Hough circle search, and then to draw a disc with the expected target size to which the image is aligned using ECC Maximization. The Hough circle detection is only accurate to a few pixels, so the ECC Maximization is needed for the final stabilization. 

Here are a couple of images showing the result of the centering/stabilization - the yellow circle is the expected target size:

<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1532335_centered_Orange.jpg" width="400">
<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1524138_centered_Blue.jpg" width="400">

Centering is turned off at closest approach by determining when the target size is over a threshold (e.g. when the diameter is over 80% of the image width). 


## Aligning Composites

Composite channels for closeup images are aligned using [feature detection][18] and matching, with [RANSAC][19] to eliminate outliers from a least-squares fit model for the translation (which amounts to the translation tx, ty between images being an average of the feature movements).

In more detail, 'interesting' features are detected using [ORB][20] in one image, and matched with their corresponding point in another image. This is done for dozens-hundreds of interest points - they are each described with a feature vector, also obtained by ORB, then matched up with their corresponding point by a brute-force search. The RANSAC algorithm is used to throw out outliers, which would otherwise throw off the determined average translation. 

If this approach fails to find a good translation (due to lack of enough corresponding points, for instance), it will fall back on [ECC Maximization][ecc] to try to align the images. 

Here is an image showing what the feature-matching process looks like, and the resulting combined image (with enhanced contrast). 

<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1637948_matching.jpg" width="800">
<img src="https://github.com/bburns/PyVoyager/raw/master/images/C1637948_aligned.jpg" width="400">



[isis]: https://isis.astrogeology.usgs.gov/
[img2png]: http://www.mmedia.is/bjj/utils/img2png/
[ffmpeg]: https://ffmpeg.org/
[ecc]: http://xanthippi.ceid.upatras.gr/people/evangelidis/ecc/

[1]: http://pds-rings.seti.org/voyager/
[3]: https://www.scipy.org/
[4]: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#cv2.HoughCircles
[5]: http://www.numpy.org/
[6]: http://matplotlib.org/
[8]: https://python-pillow.org/
[9]: https://www.continuum.io/downloads
[10]: https://pypi.python.org/pypi/tabulate
[11]: https://github.com/AndrewAnnex/SpiceyPy
[12]: http://naif.jpl.nasa.gov/naif/
[13]: https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/
[14]: https://github.com/erikrose/more-itertools
[16]: https://en.wikipedia.org/wiki/Circle_Hough_Transform
[17]: https://en.wikipedia.org/wiki/Blob_detection
[18]: https://en.wikipedia.org/wiki/Feature_detection_(computer_vision)
[19]: https://en.wikipedia.org/wiki/RANSAC
[20]: http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_orb/py_orb.html
[22]: https://www.virtualbox.org/
