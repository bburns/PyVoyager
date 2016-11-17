

"""
ISIS-related functions
"""


#. can just use cathist brief mode -
# Brief printout of a .cub history
# Description
# This example shows the cathist application in the brief mode.
# mirror from=peaks.cub to=temp.cub
# circle from=temp.cub to=temp2.cub
# Command Line
# cathist from=temp2.cub mode=brief
# Run the cahist application on a .cub file in brief mode.

def getHistory(cubefile):
    """
    get history of commands applied to given cubefile, as a list
    """

    # run ISIS cathist command
    cmd = "cathist from=%s" % cubefile
    s = lib.system(cmd)

    # parse the output
    history = []
    for line in s.split('\n'):
        if line.startswith('Object = '):
            obj = line[9:]
            history.append(obj)

    return history


def getNextRecordAndPosition(f):
    """
    Get next variable-length record from an IMQ file and the position
    of its contents in the file.
    """
    low = ord(f.read(1))
    high = ord(f.read(1))
    nbytes = high * 256 + low
    startPos = f.tell()
    s = f.read(nbytes)
    if (nbytes % 2) == 1:
        f.read(1) # read padding byte
    return s, startPos

def getImageTimeRecord(f):
    """
    Search through IMQ file records for IMAGE_TIME and return entire record
    and start file position.
    """
    imageTimeRecord = None
    startPos = None
    while True:
        s, startPos = getNextRecordAndPosition(f)
        if s.startswith('IMAGE_TIME'):
            imageTimeRecord = s
            break
        if s == 'END':
            break
    return imageTimeRecord, startPos

def getLabels(sourceFile):
    """
    Get the labels for the given IMQ file and return as a string.
    """
    f = open(sourceFile, 'rb+')
    labels = ""
    while True:
        s, pos = getNextRecordAndPosition(f)
        # print s
        labels += s + '\n'
        if s == 'END':
            break
    f.close()
    return labels

def updateImageTime(sourceFile, time):
    """
    Replace IMAGE_TIME=UNKNOWN label in the given file IMQ file with a UTC time.
    The IMQ file record fortunately has lots of spaces so can fit the
    new time into it.
    """
    f = open(sourceFile, 'rb+')
    imageTimeRecord, startPos = getImageTimeRecord(f)
    if imageTimeRecord.endswith('UNKNOWN') or imageTimeRecord.endswith('?'):
        # print "IMAGE_TIME is UNKNOWN - replacing with time value from dbFiles.csv"
        # print sourceFile
        # print imageTimeRecord
        # print time
        # print startPos
        newImageTimeRecord = 'IMAGE_TIME = ' + time + 'Z'
        nspaces = len(imageTimeRecord) - len(newImageTimeRecord)
        newImageTimeRecord += ' ' * nspaces
        # print newImageTimeRecord
        f.seek(startPos)
        f.write(newImageTimeRecord)
        # print
    f.close()




