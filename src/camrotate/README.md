
camrotate

Rotates camera matrix for an ISIS cube file

Compilation:

$ . setpaths.sh
$ make

Note: when I first compiled this it found the xml file without a problem,
but now it looks for it in an Isis xml folder, so I just copied it there.

$ cp camrotate.xml $ISISROOT/bin/xml

So for now, if update xml file, copy it there.


Usage:

$ camrotate from=foo.cub horizontal=20 vertical=0 twist=0





