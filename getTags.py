
from instagram.client import InstagramAPI
from flask import  session
import json
import types
import datetime
import ConfigParser
import datetime

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
				print "tag_name:", tag_name
				recent_media, next = self.api.user_recent_media(user_id=tag_name,max_id = session['max_tag_id'])
			
			else:
				recent_media, next = self.api.tag_recent_media(tag_name=tag_name,max_tag_id = session['max_tag_id'])

			if next is None:
				print "quitting: ", next
				return json.dumps(self.media_list)
	
			print "next url is ", next
			mag_tax_id = next.split("&")[1].split("=")[1]
			session['max_tag_id'] = mag_tax_id
              		for rm in recent_media:
                        	tag_info = {}
				if(rm.type == "video"):
					tag_info["serial_no"] = int(len(self.media_list) + 1) 	
					tag_info["tag_url"] = rm.get_standard_resolution_url()
                        		tag_info["full_name"] = rm.user.full_name + " (" + rm.user.id + ")"
                        		tag_info["profile_picture"] = rm.user.profile_picture
                        		tag_info["created_time"] = self.differenceBetweenDates(rm.created_time) + " ago, <br>" + datetime.datetime.strptime(str(rm.created_time), '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S %b %d %Y')
                        		tag_info["text"] = rm.caption.text
					if(len(self.media_list) == int(self.videos_size)):
						break
					else:
                        			self.media_list.append(tag_info)
			print "len(self.media_list)", len(self.media_list)
			#while (len(self.media_list) < 30):
			if (len(self.media_list) < int(self.videos_size)):
				self.getTags(tag_name=tag_name)
       	       		return json.dumps(self.media_list)
		except Exception,e:
			return json.dumps(self.media_list)

	def differenceBetweenDates(self,created_time):
		t2 = datetime.datetime.now()
                diff = t2 - created_time;
		diff =str(diff)
		if len(diff.split(",")) > 1:
			return diff.split(",")[0]
		else:
			l = diff.split(":")
			h = l[0]
			m = l[1]
			s = l[2].split(".")[0]
			if( int(h) > 0):
				return h + " hours"
			elif ( int(m) >  0):
				return m + " minutes"
			else:
				return s + " seconds"

