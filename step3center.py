
# center images on planet

import os

import config
import lib
import libimg


prefix = 'centered_'


def center_volume(volnumber):
    
    pngpath = lib.get_pngpath(volnumber)
    centeredpath = lib.get_centeredpath(volnumber)
    
    if os.path.isdir(centeredpath):
        print "Folder exists: " + pngpath
        return False
    else:
        try:
            os.mkdir(centeredpath) 
        except:
            pass
        for root, dirs, files in os.walk(pngpath):
            for filename in files:
                ext = filename[-4:]
                if ext=='.png':
                    infile = pngpath + '/' + filename
                    print infile
                    outfile = centeredpath + '/' + prefix + filename
                    # print '  ' + outfile
                    libimg.center_image_file(infile, outfile)

                    # im = mpim.imread(infile) # load image
                    # im = np.rot90(im, 2) # rotate by 180

                    # sums = np.sum(im, axis=0)
                    # # sums = np.sum(im, axis=1)
                    # diff = np.diff(sums)
                    # diffsq = np.square(diff)
                    # diffsqln = np.log(diffsq)
                    # N=5
                    # smoothed = np.convolve(diffsqln, np.ones((N,))/N, mode='valid')
                    # # icenter = v.find_center_1d(smoothed, 0)
                    # plt.figure(1)
                    # plt.subplot(2,1,1)
                    # plt.plot(diffsqln)
                    # plt.subplot(2,1,2)
                    # plt.plot(smoothed)
                    # plt.show()

                    # imcrop = v.center_image(im, True)

                    # # draw crosshairs
                    # imcrop[399, 0:799] = 0.5
                    # imcrop[0:799, 399] = 0.5

                    # outfile = args.prefix + infile
                    # misc.imsave(outfile, imcrop)

        return True


def main():
    # center a certain number of volumes
    n = config.nvolumes_to_center
    for volume in config.volumes:
        if n>0:
            if center_volume(volume):
                n -= 1
                
if __name__ == '__main__':
    main()


