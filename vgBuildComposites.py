

import csv

import config
# import lib

#. re-add these
# C1537734.composite,C1537734.center,Blue,1
# C1537734.composite,C1537736.center,Orange,1
# C1537734.composite,C1537738.center,Green,1
# C1537740.composite,C1537740.center,Blue,1
# C1537740.composite,C1537742.center,Orange,1
# C1537740.composite,C1537744.center,Green,1


def buildComposites(volnum):
    "build composite images by combining channel images"
    # eg
    # composites: 
    # compositeId,childId,filter,weight
    # C1537728.composite,C1537728.center,Blue,1
    # C1537728.composite,C1537730.center,Orange,1
    # C1537728.composite,C1537732.center,Green,1
    # files:
    # VGISS_5103,C1537728,Jupiter,Voyager1,Jupiter,Narrow,BLUE,3 COLOR ROTATION MOVIE
    # VGISS_5103,C1537730,Jupiter,Voyager1,Jupiter,Narrow,ORANGE,3 COLOR ROTATION MOVIE
    # VGISS_5103,C1537732,Jupiter,Voyager1,Jupiter,Narrow,GREEN,3 COLOR ROTATION MOVIE
    
    # iterate over composites.txt records
    filein = open(config.compositesdb,'rt')
    reader = csv.reader(filein)
    i = 0
    startId = ''
    channels = []
    for row in reader:
        if i==0:
            fields = row
        else:
            # row = [field.strip() for field in row]
            # print row
            volume = row[0]
            if str(volnum)==volume: #. slow
                compositeId = row[1]
                centerId = row[2]
                if compositeId == startId:
                    channels.append(row)
                else:
                    # print channels
                    # print 'process',channels
                    if len(channels)>0:
                        combineChannels(channels)
                    startId = compositeId
                    channels = [row]
        i += 1
    # print 'process remainder', channels
    combineChannels(channels)
            

def combineChannels(channels):
    # r, g, and b are 512x512 float arrays with values >= 0 and < 1.
    # from PIL import Image
    # import numpy as np
    # rgbArray = np.zeros((512,512,3), 'uint8')
    # rgbArray[..., 0] = r*256
    # rgbArray[..., 1] = g*256
    # rgbArray[..., 2] = b*256
    # img = Image.fromarray(rgbArray)
    # img.save('myimg.jpeg')
    print 'combine channels', channels
    # read those n images
    # b = cv2.imread()
    # img = cv2.merge((b,g,r))
    
    
    

if __name__ == '__main__':
    buildComposites(5101)
    print 'done'
