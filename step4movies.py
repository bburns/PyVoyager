

# copy centered pngs to movie folder, renaming/numbering them
# use ffmpeg to make the mp4 file
# wasteful but will do for now
import os

import config
import lib

volnum = 5102
voltitle = lib.get_volume_title(volnum)
src = config.centered_folder + '/' + voltitle
print src

dst = config.movie_folder + '/' + voltitle

try:
    os.mkdir(dst)
except:
    pass

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

        
#     for subdir in dirs:
#         dirpath = os.path.join(root, subdir)
#         dirpath = os.path.abspath(dirpath)
#         print dirpath
#         img2png(dirpath)








