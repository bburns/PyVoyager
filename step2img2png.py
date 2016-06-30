
# convert voyager img files to png, using img2png
# --------------------------------------------------------------------------------

# currently,
# cd to the datavolume, eg VGISS_5101
# > vr unzip
# by default it'll start in the data dir, and convert all "*raw.img" files to pngs,
# appending the filter name. 

startdirdefault = "data"
filespecdefault = "*raw.img"
img2png_options = "-fnamefilter"

def getargs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--recurse", help="recurse through child folders", action="store_true")
    parser.add_argument("filespec", nargs="?", help="file specifier, like *raw.img") #. diff linux and win
    args = parser.parse_args()
    return args

def img2png(dirpath):
    import os
    savedir = os.getcwd()
    os.chdir(dirpath)
    # eg "img2png *.img -fnamefilter"
    cmd = "img2png " + filespec + " " + img2png_options
    print cmd
    os.system(cmd)
    os.chdir(savedir)


def main:
    # parse command line arguments    
    args = getargs()
    
    # if args.recurse:
    #     print "recursing"
    
    # for each dir in thisdir, cd dir, run img2png
    import os
    for root, dirs, files in os.walk(startdir):
        # for name in files:
            # print(os.path.join(root, name))
        for name in dirs:
            dirpath = os.path.join(root, name)
            dirpath = os.path.abspath(dirpath)
            print dirpath
            img2png(dirpath)


main()
