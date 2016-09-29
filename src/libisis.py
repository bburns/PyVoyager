

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



