
from instagram.client import InstagramAPI

class TagMedia:

	def __init__(self):
		self.access_token = "36207530.e2b196f.fc6b55f228d04f3bbb110629f4b1cc19"
		self.api = InstagramAPI(access_token=self.access_token)

	def getTags(self,tag_name):
		recent_media, next = self.api.tag_recent_media(tag_name="snow", count=10)
		return recent_media
