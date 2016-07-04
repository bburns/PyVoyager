

# copy centered pngs to movie folder, renaming/numbering them
# use ffmpeg to make the mp4 file
#... wasteful but will do for now

import os

import config
import lib



def makeMovieVolume(volnum):
    ""
    voltitle = lib.getVolumeTitle(volnum)
    src = config.centeredFolder + '/' + voltitle
    dst = config.movieFolder + '/' + voltitle
    if volnum!=0 and os.path.isdir(dst):
        print "Folder exists: " + dst
        return False
    else:
        try:
            os.mkdir(dst)
        except:
            pass
        # copy files, numbering them sequentially
        i = 0
        for root, dirs, files in os.walk(src):
            for infile in files:
                inpath = src + '/' + infile
                # print inpath
                outfile = 'img%04d.png' % i
                outpath = dst + '/' + outfile
                # print outpath
                i += 1
                cmd = "cp " + inpath + " " + outpath
                print cmd
                os.system(cmd)
        # now make movie with ffmpeg
        movieName = voltitle + '.mp4'
        lib.pngsToMp4(dst, 'img%04d.png', config.frame_rate, movieName)
        return True

        
def main():
    # makeMovieVolume(0)
    
    # center a certain number of volumes
    n = config.nvolumesToMovieize
    for volume in config.volumes:
        if n>0:
            if makeMovieVolume(volume):
                n -= 1
                
if __name__ == '__main__':
    main()


