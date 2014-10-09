import requests
import json
import hashlib
import datetime
from pytz import timezone

def convertToPTTimezone(created_time, fmt='%Y-%m-%d %H:%M:%S'):
  datetime_obj = datetime.datetime.strptime(str(created_time), fmt)
  datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))
  now_pacific = datetime_obj_utc.astimezone(timezone('US/Pacific'))
  return (now_pacific)


def differenceBetweenDates(created_time, fmt):
  t2 = datetime.datetime.now(timezone('US/Pacific'))
  t1 = convertToPTTimezone(created_time, fmt)
  diff = t2 - t1
  diff =str(diff)
  # print "difference is ", diff
  if len(diff.split(",")) > 1:
    return diff.split(",")[0]
  else:
    l = diff.split(":")
    h = l[0]
    m = l[1]
    s = l[2].split(".")[0]
    if( int(h) > 0):
      return h + " hour(s)"
    elif ( int(m) >  0):
      return m + " minute(s)"
    else:
      return s + " second(s)"
