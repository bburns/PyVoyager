

s = """
# this is a comment

imageId,x,y
c1239135,123,54

# another comment
c7342573,941,23
"""

# want to iterate over the lines of the string, skipping the header, comments, and blank lines
# write a generator



def dataLines(lines):
    "a generator that excludes comments, blank lines, and the header (first data row) from lines"
    i = 0
    for line in lines:
        line = line.strip()
        if line and line[0]!='#':
            if i>0:
                yield line
            i += 1



lines = s.split('\n')
print lines

for dl in dataLines(lines):
    print dl


# so could use this to wrap a file to just return the data rows

