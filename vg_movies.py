

# copy centered pngs to movie folder, renaming/numbering them
# use ffmpeg to make the mp4 file
# wasteful but will do for now

import os

import config
import lib


def makeMovieVolume(volnum):
    "Make an mp4 movie for the given volume"
    voltitle = lib.getVolumeTitle(volnum) # eg VGISS_5101
    src = config.centersFolder + '/' + voltitle
    dst = config.moviesFolder + '/' + voltitle
    if volnum!=0 and os.path.isdir(dst):
        print "Folder exists: " + dst
        return False
    else:
        # stage files for ffmpeg
        filenamePattern = 'img%04d.png'
        lib.copyFilesSequenced(src, dst, filenamePattern)
        # now make movie with ffmpeg
        movieName = '_' + voltitle + '.mp4' # prepend _ so sorts at start of file list
        lib.pngsToMp4(dst, filenamePattern, movieName, config.frameRate)
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


