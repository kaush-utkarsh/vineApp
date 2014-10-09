import ConfigParser

VINE_API_BASE_URL = "https://api.vineapp.com/"

config = ConfigParser.ConfigParser()
config.read('config.txt')
VIDEOS_LIMIT = config.get('system_section','size')
ACCESS_TOKEN = "36207530.e2b196f.fc6b55f228d04f3bbb110629f4b1cc19"