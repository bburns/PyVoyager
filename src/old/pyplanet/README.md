

obsolete - moved into pyvoyager




pyplanet
--------------------------------------------------------------------------------

python package with some image processing functions to detect and center planet images
used by pyvoyager

- find_center_by_box - find largest (partially occluded) circle/ellipse in image, and return x,y,xradius,yradius. use bounding box detection
- find_center_by_blob - find largest (partially occluded) circle/ellipse in image, and return x,y,xradius,yradius. use image lib blob detection
- center_image - center an image on x,y coordinates
- draw_bounding_box - draw a bounding box on image




