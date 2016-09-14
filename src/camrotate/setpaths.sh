
if [ -z "$SPICEROOT" ]
then
	echo Please set SPICEROOT
fi

CPATH=/usr/include/qt4
CPATH=$CPATH:/usr/include/qt4/Qt
CPATH=$CPATH:/usr/include/qt4/QtCore
CPATH=$CPATH:/usr/include/qt4/QtGui
CPATH=$CPATH:$SPICEROOT/include
export CPATH

LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
LIBRARY_PATH=$LIBRARY_PATH:$ISISROOT/lib
LIBRARY_PATH=$LIBRARY_PATH:$ISISROOT/3rdParty/lib
export LIBRARY_PATH

