
"""
Generate framerates.csv records for voyager 1 red spot approach movie
"""

import os

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg


os.chdir('../..')

csvComposites,f = lib.openCsvReader(config.dbComposites)
group = 0
channel = 0

# for c='C1464337'...'C1534823'
for row in csvComposites:

    compositeId = row[config.colCompositesCompositeId]
    fileId = row[config.colCompositesFileId]
    filter = row[config.colCompositesFilter]

    if compositeId<'C1464337': continue # start here
    if compositeId>'C1534823': break # stop here

    if filter=='Clear': continue # Clear channels thrown in there every now and then

    # if compositeId=='C1494354': channel=1 # missed the Uv channel
    if fileId=='C1494354': channel=1 # missed the Uv channel
    if fileId=='C1507521': group=4; channel=0 # redspot - skip previous gaps

    # first group - turn off
    if group==0 and channel==0:
        print compositeId + '+,0'

    # fourth group - turn on - this group has the red spot
    if group==4 and channel==0:
        print compositeId + ',2'
        # print compositeId + ',1'

    if fileId=='C1527353': channel=1 # missed the uv channel
    if fileId=='C1532333': channel=2 # missed uv and blue channels

    # next channel/group
    channel += 1
    if channel>3:
        channel = 0
        group += 1
        if group>4:
            group = 0

f.close()

