

# copy centered pngs to movie folder, renaming/numbering them
# use ffmpeg to make the mp4 file
# wasteful but will do for now

import os

import config
import lib

def copyFiles(src, dst):
    try:
        os.mkdir(dst)
    except:
        pass
    # copy files, numbering them sequentially
    # (wasteful, but necessary as ffmpeg doesn't handle globbing on windows)
    i = 0
    for root, dirs, files in os.walk(src):
        for infile in files:
            inpath = src + '/' + infile
            # print inpath
            outfile = 'img%04d.png' % i
            outpath = dst + '/' + outfile
            # print outpath
            i += 1
            # print 'copy ' + str(i) + ': ' + inpath
            cmd = "cp " + inpath + " " + outpath
            # print cmd
            os.system(cmd)
            print 'copied ' + str(i) + ': ' + outpath
    


def makeMovieVolume(volnum):
    ""
    voltitle = lib.getVolumeTitle(volnum)
    src = config.centeredFolder + '/' + voltitle
    dst = config.movieFolder + '/' + voltitle
    if volnum!=0 and os.path.isdir(dst):
        print "Folder exists: " + dst
        return False
    else:
        copyFiles(src, dst)
        # now make movie with ffmpeg
        movieName = '_' + voltitle + '.mp4' # prepend _ so sorts at start of file list
        lib.pngsToMp4(dst, 'img%04d.png', config.frameRate, movieName)
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


