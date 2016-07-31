
# combine channels to make composite images

import cv2
import numpy as np


# this works

# # load images
# b=cv2.imread('composites/blue.png',cv2.IMREAD_GRAYSCALE)
# r=cv2.imread('composites/orange.png',cv2.IMREAD_GRAYSCALE)
# g=cv2.imread('composites/green.png',cv2.IMREAD_GRAYSCALE)

# # apply weights
# b = cv2.multiply(b,0.7)
# r = cv2.multiply(r,0.5)
# # g = cv2.multiply(g,1.0)

# # merge channels
# img = cv2.merge((b,g,r))

# # show image
# cv2.imshow("output",img)
# cv2.waitKey(0)


# put into a fn...

def combineChannels(channels):
    "combine the given weighted channels and return a single image"
    # eg channels = {
    # 'Orange':'composites/orange.png',
    # 'Green':'composites/green.png',
    # 'Blue':'composites/blue.png',
    # }
    # if missing a channel will use a blank/black image for that channel
    
    # get filenames
    redfile = channels.get('Orange')
    greenfile = channels.get('Green') or channels.get('Clear')
    bluefile = channels.get('Blue') or channels.get('Violet') or channels.get('Ultraviolet')
    
    # read images
    # returns None if filename is invalid - doesn't throw an error
    red = cv2.imread(redfile,cv2.IMREAD_GRAYSCALE)
    green = cv2.imread(greenfile,cv2.IMREAD_GRAYSCALE)
    blue = cv2.imread(bluefile,cv2.IMREAD_GRAYSCALE)
    
    # assign a blank image if missing a channel
    blank = np.zeros((800,800), np.uint8)
    if red is None: red = blank
    if green is None: green = blank
    if blue is None: blue = blank
    
    # apply weights
    blue = cv2.multiply(blue,0.6)
    red = cv2.multiply(red,0.5)
    # green = cv2.multiply(green,1.0)

    # merge channels - BGR for cv2
    im = cv2.merge((blue, green, red))
    
    return im


channels = {
    'Orange':'composites/orange.png',
    'Green':'composites/green.png',
    'Blue':'composites/blue.png',
    }
im = combineChannels(channels)
cv2.imshow("output",im)
cv2.waitKey(0)



# b=cv2.imread('composites/blue.png')
# r=cv2.imread('composites/orange.png')
# g=cv2.imread('composites/green.png')
# b = cv2.applyColorMap(b, cv2.COLORMAP_RAINBOW)
# img = cv2.addWeighted(b,0.6,r,0.4)
# img = cv2.add(b,r)
# img=b


print 'done'

