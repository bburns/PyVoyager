
Volume Indexes
--------------

Each VGISS volume includes the file rawimages.tab in /index,
which is the complete index for the flybys of that planet -
e.g. volume 5101 rawimages.tab includes all of Voyager 1 and 2 at Jupiter.

They were copied here, with a suffix indicating the planet:
5 Jupiter  
6 Saturn  
7 Uranus  
8 Neptune  


Columns (extracted from rawimages.lbl):

VOLUME_NAME
FILE_SPECIFICATION_NAME
PRODUCT_ID
PRODUCT_TYPE
INSTRUMENT_HOST_NAME
MISSION_PHASE_NAME
TARGET_NAME
IMAGE_ID
IMAGE_NUMBER
IMAGE_TIME
EARTH_RECEIVED_TIME
INSTRUMENT_NAME
SCAN_MODE
SHUTTER_MODE
GAIN_MODE
EDIT_MODE
FILTER_NAME
FILTER_NUMBER
EXPOSURE_DURATION
NOTE
SAMPLE_BIT_MASK
DATA_ANOMALY


in more detail:

     NAME                       = VOLUME_NAME
     COLUMN_NUMBER              = 1
     FORMAT                     = "A10"
     DESCRIPTION                = "The PDS identification for this volume."

     NAME                       = FILE_SPECIFICATION_NAME
     COLUMN_NUMBER              = 2
     FORMAT                     = "A34"
     DESCRIPTION                = "The name and directory path of the PDS
label file describing this particular file or files."

     NAME                       = PRODUCT_ID
     COLUMN_NUMBER              = 3
     FORMAT                     = "A20"
     DESCRIPTION                = "The unique identifier assigned to the data
product. In this data set, it is equivalent to the file name without the
directory path. In cases where a combined-detached label describes two files,
this is the name of the binary file (ending in '.DAT'); the corresponding
ASCII text file (ending in '.TAB') is not listed in the index."

     NAME                       = PRODUCT_TYPE
     COLUMN_NUMBER              = 4
     FORMAT                     = "A29"
     DESCRIPTION                = "Description of the type of data file, one
of: BLEMISH_TABLE, CALIBRATED_IMAGE, CALIBRATION_MODEL, CLEANED_IMAGE,
DARK_CURRENT_IMAGE, TIEPOINT_TABLE, GEOMETRICALLY_CORRECTED_IMAGE,
DECOMPRESSED_RAW_IMAGE, or RESEAU_TABLE."

     NAME                       = INSTRUMENT_HOST_NAME
     COLUMN_NUMBER              = 5
     FORMAT                     = "A9"
     DESCRIPTION                = "The spacecraft name associated with the
image, either VOYAGER 1 and VOYAGER 2."

     NAME                       = MISSION_PHASE_NAME
     COLUMN_NUMBER              = 6
     FORMAT                     = "A17"
     DESCRIPTION                = "Name of mission phase for this image, one
of JUPITER ENCOUNTER, SATURN ENCOUNTER, URANUS ENCOUNTER, or NEPTUNE
ENCOUNTER."

     NAME                       = TARGET_NAME
     COLUMN_NUMBER              = 7
     FORMAT                     = "A10"
     DESCRIPTION                = "The nominal or intended primary target 
of the observation. The values in this column are occasionally incorrect 
and frequently are not comprehensive. The values given are based on 
information in the original data file label. In some cases the nominal 
target was misidentified. Further, while only one target is listed, many 
images contain multiple targets within the field of view."

     NAME                       = IMAGE_ID
     COLUMN_NUMBER              = 8
     FORMAT                     = "A10"
     DESCRIPTION                = "
Image identification, which takes the form: nnnnes+ddd, where 'nnnn' = picture sequence number for a given day, 'e' = planet of encounter (J=Jupiter, S=Saturn, U=Uranus, N=Neptune), 's' = Voyager spacecraft (1 or 2), - sign indicates before and a + sign indicates after closest planetary approach, 'ddd' = number of days from closest approach."

Image identification: nnnnes+ddd, where nnnn=picture sequence number for a given day, e=planet of encounter (J,S,U,N), s=Voyager 1 or 2, - indicates before and + indicates after closest planetary approach, ddd=number of days from closest approach.


     NAME                       = IMAGE_NUMBER
     COLUMN_NUMBER              = 9
     FORMAT                     = "F8.2"
     DESCRIPTION                = "The unique number which identifies this image. IMAGE_NUMBER is extracted from the Flight Data Subsystem (FDS) clock count at time of image acquisition. For Voyager images the number is a seven-digit value, with 5 digits to the left of the decimal point (the modulo 16-bit (65536) count and 2 digits to the right of the decimal point (the modulo 60 count)."
     DESCRIPTION                = "The unique number which identifies this image. extracted from Flight Data Subsystem (FDS) clock count at time of image acquisition. 7-digit value, 5 to the left of decimal point (modulo 16-bit (65536) count and 2 to the right (modulo 60 count)."


     NAME                       = IMAGE_TIME
     COLUMN_NUMBER              = 10
     FORMAT                     = "A19"
     DESCRIPTION                = "Time at which image was acquired, in the format yyyy-mm-ddThh:mm:ss.  The time system is Universal Time (UTC). 'yyyy' for year, 'mm' for month, 'dd' for day of month, 'hh' for hour, 'mm' for minute, 'ss' for second."

     NAME                       = EARTH_RECEIVED_TIME
     COLUMN_NUMBER              = 11
     FORMAT                     = "A19"
     DESCRIPTION                = "Time at which image data was received on earth, in the format yyyy-mm-ddThh:mm:ss. The time system is Universal Time (UTC). 'yyyy' = year, 'mm' = month, 'dd' = day of month, 'hh' = hour, 'mm' = minute, 'ss' = second."

     NAME                       = INSTRUMENT_NAME
     COLUMN_NUMBER              = 12
     FORMAT                     = "A19"
     DESCRIPTION                = "The camera used to acquire the image, either NARROW ANGLE CAMERA or WIDE ANGLE CAMERA."

     NAME                       = SCAN_MODE
     COLUMN_NUMBER              = 13
     FORMAT                     = "A4"
     DESCRIPTION                = "
The scan rate of vidicon readout. Values can be '1:1', '2:1', '3:1', '5:1', and '10:1'. The instrument scan rate affects the radiometric properties of the camera because of the dark current buildup on the vidicon."

     NAME                       = SHUTTER_MODE
     COLUMN_NUMBER              = 14
     FORMAT                     = "A6"
     DESCRIPTION                = "The instrument shutter mode, one of:
   NAONLY - narrow angle camera shuttered only;
   WAONLY - wide angle camera shuttered only;
   BOTSIM - both cameras shuttered simultaneously;
   BOTALT - both cameras shuttered alternately;
   BSIMAN - BOTSIM mode followed by NAONLY;
   BODARK - shutter remained closed for entire exposure time.
"
The instrument shutter mode: NAONLY - narrow angle camera only; WAONLY - wide angle camera only; BOTSIM - both cameras simultaneously; BOTALT - both cameras alternately; BSIMAN - BOTSIM mode followed by NAONLY; BODARK - shutter closed.
   

     NAME                       = GAIN_MODE
     COLUMN_NUMBER              = 15
     FORMAT                     = "A4"
     DESCRIPTION                = "The gain mode (LOW or HIGH, typically LOW) of the camera."

     NAME                       =   EDIT_MODE
     COLUMN_NUMBER              = 16
     FORMAT                     = "A4"
     DESCRIPTION                = "
The edit mode of the camera. Values are '1:1', which indicates the full resolution of the vidicon, and '3:4', '3:5', '1:2', '2:5', '1:3', '1:5', and '1:10' for partial resolution images. This indicates the amount of data read from the vidicon."

     NAME                       = FILTER_NAME
     COLUMN_NUMBER              = 17
     FORMAT                     = "A6"
     DESCRIPTION                = "The optical filter used for the image, one of CLEAR, CH4_U, CH4_JS, UV, VIOLET, BLUE, GREEN, ORANGE, and SODIUM."

     NAME                       = FILTER_NUMBER
     COLUMN_NUMBER              = 18
     FORMAT                     = "I1"
     DESCRIPTION                = "
The optical filter number (0-7), which contains the unique number associated with the optical filter for the image. It is needed to differentiate between the two CLEAR and two GREEN filters on the Voyager narrow angle camera."

     NAME                       = EXPOSURE_DURATION
     COLUMN_NUMBER              = 19
     FORMAT                     = "F9.4"
     DESCRIPTION                = "Exposure duration for the image, in seconds."
     NULL_CONSTANT              = -99.9999

     NAME                       = NOTE
     COLUMN_NUMBER              = 20
     FORMAT                     = "A80"
     DESCRIPTION                = "A brief comment about the image. The information in this field was transferred from the original data files. We were unable to verify the validity of the information although we do know that in some cases it is incorrect."

     NAME                       = SAMPLE_BIT_MASK
     COLUMN_NUMBER              = 21
     FORMAT                     = "A8"
     DESCRIPTION                = "The character string contains ones and zeros to indicate the active bits in each sample of the raw image. If the bits are all active, then the mask is '11111111'."

     NAME                       = DATA_ANOMALY
     COLUMN_NUMBER              = 22
     FORMAT                     = "A6"
     DESCRIPTION                = "A text field which identifies anomalies associated with an image. NONE indicates no anomalies were detected. A value of RAMCOR indicates that spurious values exist in the image data due to corruption of the random access memory onboard the spacecraft.

