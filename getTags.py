from instagram.client import InstagramAPI
from flask import  session
import json
import types
import datetime
import ConfigParser
import datetime
from pytz import timezone
import pytz

class TagMedia:

  def __init__(self):
    # Parse the arguments
    config = ConfigParser.ConfigParser()
    config.read('config.txt')
    self.videos_size = config.get('system_section','size')
    self.access_token = "36207530.e2b196f.fc6b55f228d04f3bbb110629f4b1cc19"
    self.api = InstagramAPI(access_token=self.access_token)
    self.media_list = []

  def getTags(self,tag_name):
    try:
      if tag_name.isdigit():
        # print "tag_name:", tag_name
        recent_media, next = self.api.user_recent_media(user_id=tag_name,max_id = session['max_tag_id'])

      else:
        recent_media, next = self.api.tag_recent_media(tag_name=tag_name,max_tag_id = session['max_tag_id'])

      if next is None:
        # print "quitting: ", next
        return json.dumps(self.media_list)

      # print "next url is ", next
      mag_tax_id = next.split("&")[1].split("=")[1]
      session['max_tag_id'] = mag_tax_id
      for rm in recent_media:
        tag_info = {}
        if(rm.type == "video"):
          try:
            # print "rm.created_time...", rm.created_time
            # print "converted time" , self.convertToPTTimezone(rm.created_time)
            tag_info["serial_no"] = int(len(self.media_list) + 1)
            tag_info["tag_url"] = rm.get_standard_resolution_url()
            tag_info["full_name"] = rm.user.username + " (" + rm.user.id + ") <br>" + rm.user.full_name
            tag_info["profile_picture"] = rm.user.profile_picture
            tag_info["created_time"] = (self.differenceBetweenDates(rm.created_time) + " ago, <br>" + self.convertToPTTimezone(rm.created_time).strftime('%H:%M:%S %b %d %Y')).replace("-", "")
            tag_info["text"] = rm.caption.text
            tag_info["tag"] = tag_name
            tag_info["id"] = rm.id
            if(len(self.media_list) == int(self.videos_size)):
              break
            else:
              self.media_list.append(tag_info)
          except:
            continue
      # print "len(self.media_list)", len(self.media_list)
      #while (len(self.media_list) < 30):
      if (len(self.media_list) < int(self.videos_size)):
        self.getTags(tag_name=tag_name)
      return json.dumps(self.media_list)
    except Exception,e:
      import traceback
      # print traceback.print_exc()
      return json.dumps(self.media_list)

  def convertToPTTimezone(self,created_time):
    fmt  = '%Y-%m-%d %H:%M:%S'
    datetime_obj = datetime.datetime.strptime(str(created_time), fmt)
    datetime_obj_utc = datetime_obj.replace(tzinfo=timezone('UTC'))
    now_pacific = datetime_obj_utc.astimezone(timezone('US/Pacific'))
    return (now_pacific)


  def differenceBetweenDates(self,created_time):
    fmt  = '%Y-%m-%d %H:%M:%S'
    t2 = datetime.datetime.now(timezone('US/Pacific'))
    t1 = self.convertToPTTimezone(created_time)
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

