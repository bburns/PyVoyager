
# text tests

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

# fontpath = "c:/windows/fonts/arial.ttf"
fontpath = "c:/windows/fonts/!futura-light.ttf"
fontsize = 48
# font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 25)
font = ImageFont.truetype(fontpath, fontsize)

imgsize = (800,800)
bgcolor = (0,0,0)
fgcolor = (200,200,200)
pos = (200,300)

img = Image.new("RGBA", imgsize, bgcolor)
draw = ImageDraw.Draw(img)

s = "Triton Flyby"
draw.text(pos, s, fgcolor, font=font)
w,h = font.getsize(s)
print w,h # 207,53

pos = (pos[0],pos[1]+h*1.5)
s = "Neptune System"
fgcolor = (120,120,120)
draw.text(pos, s, fgcolor, font=font)

pos = (pos[0],pos[1]+h)
s = "Voyager 2"
draw.text(pos, s, fgcolor, font=font)

draw = ImageDraw.Draw(img)
img.save("a_test.png")

import os
os.system("a_test.png")


    
makeTitlePage("Triton Flyby", "Neptune System", "Voyager 2")



# to draw text over an image
# see http://pillow.readthedocs.io/en/3.1.x/reference/ImageDraw.html

