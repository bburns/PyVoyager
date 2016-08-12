
# walk through volumes and histogram stretch already centered images

import os
import cv2

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg


# vols = [str(vol) for vol in range(5105,5121)]
vols = [str(vol) for vol in range(5108,5121)]
print vols

folder = '../../data/step06_centers/'
os.chdir(folder)

# for root, dirs, files in os.walk('../../data/step04_adjustments/'):
for root, dirs, files in os.walk(folder):
# for root, dirs, files in os.walk('../../data/step06_composites/'):
    # print root
    dirtitle = root.split('/')[-1]
    # print dirtitle
    if dirtitle[:5]=='VGISS':
        # print dirs
        vol = dirtitle[6:]
        os.chdir(dirtitle)
        if vol in vols:
            print vol
            for filename in files:
                if filename[-4:]=='.jpg':
                    print filename
                    im = cv2.imread(filename)
                    im = libimg.stretchHistogram(im)
                    cv2.imwrite(filename, im)
        os.chdir('..')
        print
                
lib.beep()

    # curdir = os.getcwd()
    # os.chdir(root)
    # cmd = "mogrify -format jpg *.png"
    # for filename in files:
        # im = cv2.imread(filename)
    # cmd = "rm *.png"
    # print cmd
    # os.system(cmd)
    # os.chdir(curdir)




# switch order of centers.csv columns
# reader,f = lib.openCsvReader('../../'+ config.dbCenters)
# writer,fout = lib.openCsvWriter('../../db/foo.csv')
# for row in reader:
#     row2 = list(row)
#     if row[0][0]!='C':
#         row2[0] = row[1]
#         row2[1] = row[0]
#     writer.writerow(row2)
# fout.close()
# f.close()

# # switch order of composites.csv columns
# # volume,compositeId,imageId,filter,weight,x,y
# # 5101,C1462321,C1462321,Clear
# reader,f = lib.openCsvReader('../../'+ config.dbComposites)
# writer,fout = lib.openCsvWriter('../../db/foo.csv')
# for row in reader:
#     row2 = list(row)
#     row2[0] = row[1]
#     row2[1] = row[2]
#     row2[2] = row[0]
#     writer.writerow(row2)
# fout.close()
# f.close()



