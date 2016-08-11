

# from datetime import datetime, timedelta
from datetime import datetime

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    return td.total_seconds()
    # return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

# import dateutil
from dateutil import parser
snow = "1986-01-18T15:35:10"
now = parser.parse(snow)

# now = datetime.utcnow()
print now
print totimestamp(now)

