

import sys; sys.path.append('..') # so can import from main src folder
import config
import lib
import libimg


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

# switch order of composites.csv columns
# volume,compositeId,imageId,filter,weight,x,y
# 5101,C1462321,C1462321,Clear
reader,f = lib.openCsvReader('../../'+ config.dbComposites)
writer,fout = lib.openCsvWriter('../../db/foo.csv')
for row in reader:
    row2 = list(row)
    row2[0] = row[1]
    row2[1] = row[2]
    row2[2] = row[0]
    writer.writerow(row2)
fout.close()
f.close()



