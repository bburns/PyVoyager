
# image processing routines


import matplotlib.image as mpim # for imread
import scipy.misc as misc # for imsave
import numpy as np # for zeros, array, copy


def center_image_file(infile, outfile, rotate_image=False):
    "center the given image file on a planet"
    im = mpim.imread(infile)
    if rotate_image:
        im = np.rot90(im, 2) # rotate by 180
    #. if use_blobs:
    # bounding_box = find_center_by_blob(im)
    bounding_box = find_center_by_box(im)
    im = draw_bounding_box(im, bounding_box)
    im_centered = center_image(im, bounding_box)
    # draw crosshairs
    if config.draw_crosshairs:
        im_centered[399, 0:799] = 0.25
        im_centered[0:799, 399] = 0.25
    misc.imsave(outfile, im_centered)
    return True
    

def center_image(im, bounding_box):
    "center image on bounding box, crop to it, return new image"
    
    # cx, cy = find_center_by_blob(im)
    # cx, cy = find_center_by_edges(im)
    # x1,x2,y1,y2 = find_object_edges(im)
    [x1,y1,x2,y2] = bounding_box
    cx = (x1+x2)/2.0
    cy = (y1+y2)/2.0
    
    imwidth = im.shape[0]
    imheight = im.shape[1]
    
    # make a bigger canvas to place image im on
    newsize = (imwidth * 2, imheight * 2)
    canvas = np.zeros(newsize)
    
    # put image on canvas centered on bounding box
    # eg canvas[800-cx:1600-cx, 800-cy:1600-cy] = np.array(im)
    canvas[imwidth-cx : imwidth-cx+imwidth, imheight-cy : imheight-cy+imheight] = np.array(im)

    # crop canvas to original image size
    # eg imcrop = canvas[400:1200, 400:1200]
    imcrop = canvas[imwidth/2 : imwidth/2+imwidth, imheight/2 : imheight/2+imheight]
    
    return imcrop


def draw_bounding_box(im, bounding_box):
    "draw a box on image, return new image"
    
    [x1,y1,x2,y2] = bounding_box
    
    im_bb = np.copy(im)
    
    c = 0.5
    im_bb[x1:x2,y1] = c
    im_bb[x1:x2,y2] = c
    im_bb[x1,y1:y2] = c
    im_bb[x2,y1:y2] = c
    
    #. or this, but what is plt?
    # plt.gca().add_patch(patches.Rectangle((y1,x1), y2-y1, x2-x1, fill=False, edgecolor="green", linewidth=0.5))
    
    return im_bb



def find_center_by_blob(im):
    "Find the largest blob in the given image and return the bounding box [x1,y1,x2,y2]"
    
    # for blob detection
    import scipy.ndimage as ndimage # for measurements, find_objects

    def find_blobs(im):
        "Find set of blobs in the given image"
        epsilon = 0.1
        b = 1*(im>epsilon) # threshold to binary image
        lbl, nobjs = ndimage.measurements.label(b) # label objects
        # find position of objects - index is 0-based
        blobs = ndimage.find_objects(lbl)
        return blobs

    def find_largest_blob(blobs):
        "Find largest blob in the given array of blobs"
        widthmax = 0
        heightmax = 0
        for blob in blobs:
            width = blob[0].stop - blob[0].start
            height = blob[1].stop - blob[1].start
            if width>widthmax and height>heightmax:
                widthmax = width
                heightmax = height
                largest = blob
        return largest

    blobs = find_blobs(im)
    if len(blobs)>0:
        # find largest object
        blob = find_largest_blob(blobs)
        # get bounding box
        x1 = blob[0].start
        x2 = blob[0].stop
        y1 = blob[1].start
        y2 = blob[1].stop
    else:
        # if no blobs just return the whole image
        x1 = 0
        x2 = im.shape[0] - 1
        y1 = 0
        y2 = im.shape[1] - 1
    return [x1,y1,x2,y2]



#. cheat for now
import config


# def find_center_by_box(im, epsilon=0, N=5):
def find_center_by_box(im):
    "find edges of largest object in image based on the most prominent edges, and return bounding box"

    # def find_edges_1d(a, epsilon = 0):
    def find_edges_1d(array):
        "find edges>epsilon in 1d array from left and right directions, return first,last indexes"
        icount = len(array)
        istart = 4 #. why skip 4?
        iend = icount
        # epsilon is the threshold value over which the smoothed value must cross
        epsilon = config.epsilon
        # find first value over threshold
        ifirst = 0
        for i in xrange(istart, iend, 1):
            if array[i] > epsilon:
                ifirst = i
                break
        # find last value over threshold
        ilast = iend-1
        for i in xrange(iend-1, istart-1, -1):
            if array[i] > epsilon:
                ilast = i
                break
        return ifirst,ilast

    # def find_edges(im, axis, epsilon=0, N=5):
    def find_edges(im, axis):
        "find the edges for the given axis (0 or 1), return min,max"
        sums = np.sum(im, axis=axis)
        diff = np.diff(sums)
        diffsq = np.square(diff)
        diffsqln = np.log(diffsq)
        # config.N is the number of rows/columns to average over, for running average
        N = config.N
        if N>0:
            smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
            i1, i2 = find_edges_1d(smoothed)
        else:
            i1, i2 = find_edges_1d(diffsqln)
        return i1, i2

    x1, x2 = find_edges(im, 1)
    y1, y2 = find_edges(im, 0)
    
    #. now try to make it a square - could assume that the smaller one is correct...
    # because seem to get a lot of those cases
    
    bounding_box = [x1,y1,x2,y2]
    return bounding_box



# simple test

def test():
    
    infile = 'test/test.png'
    
    # load image
    im = mpim.imread(infile)
    
    # find bounding box around planet
    # bounding_box = find_center_by_blob(im)
    bounding_box = find_center_by_box(im)
    print bounding_box

    # draw bounding box, save image
    im_bb = draw_bounding_box(im, bounding_box)
    misc.imsave('test/test_bounding_box.png', im_bb)

    # center image, save image
    im_centered = center_image(im, bounding_box)
    misc.imsave('test/test_centered.png', im_centered)

    # test the center_image_file fn
    center_image_file('test/test.png', 'test/test_cif.png')
    
    print 'done.'
    
    
if __name__ == '__main__':
    test()


