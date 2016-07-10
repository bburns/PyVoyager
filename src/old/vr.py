
# vr
# voyager command handler - launch other image processing programs
# --------------------------------------------------------------------------------


import sys
args = sys.argv[1:] # remove command
nargs = len(args)
cmd = "help" if (nargs==0) else args.pop(0) # first item


# get the path of this file
# see http://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing
import os
import inspect
thispath = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

if cmd=="unzip":
    s = "python " + thispath + "/vr_to_png.py " + " ".join(args)
    # print s
    os.system(s)

elif cmd=="center":
    s = "python " + thispath + "/vr_center.py " + " ".join(args)
    # print s
    os.system(s)

elif cmd=="help":
    pass
    
else:
    print
    print "Command not recognized."
    cmd = 'help'
    
if cmd=="help":
    print
    print "voyager: image processing"
    print
    print "Commands:"
    print "  vr unzip"
    print "  vr center"
    print
    

# import argparse

# def get_parser():
#     parser = argparse.ArgumentParser(description='Voyager image processing')
#     # parser.add_argument('query', metavar='QUERY', type=str, nargs='*', help='the question to answer')
#     # parser.add_argument('-p', '--pos', help='select answer in specified position (default: 1)', default=1, type=int)
#     # parser.add_argument('-a', '--all', help='display the full text of the answer', action='store_true')
#     # parser.add_argument('-l', '--link', help='display only the answer link', action='store_true')
#     # parser.add_argument('-c', '--color', help='enable colorized output', action='store_true')
#     # parser.add_argument('-n', '--num-answers', help='number of answers to return', default=1, type=int)
#     # parser.add_argument('-C', '--clear-cache', help='clear the cache', action='store_true')
#     # parser.add_argument('-v', '--version', help='displays the current version of howdoi', action='store_true')
#     return parser


# def main():
#     parser = get_parser()
#     args = vars(parser.parse_args())
    

# if __name__ == '__main__':
#     main()
