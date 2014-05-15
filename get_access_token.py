
from instagram.client import InstagramAPI
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'local':
    try:
        from test_settings import *

        InstagramAPI.host = test_host
        InstagramAPI.base_path = test_base_path
        InstagramAPI.access_token_field = "access_token"
        InstagramAPI.authorize_url = test_authorize_url
        InstagramAPI.access_token_url = test_access_token_url
        InstagramAPI.protocol = test_protocol
    except Exception:
        pass

client_id = 'e2b196f4aeb24ce58bc5e10990cb0da5'
client_secret = '024d7e6f16aa470d8d8c274a490bb6e7'
redirect_uri = 'http://www.algoscale.com/about.html'
raw_scope = ''
scope = raw_scope.split(' ')
# For basic, API seems to need to be set explicitly
if not scope or scope == [""]:
    scope = ["basic"]

api = InstagramAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
redirect_uri = api.get_authorize_login_url(scope = scope)

print "Visit this page and authorize access in your browser:\n", redirect_uri

code = raw_input("Paste in code in query string after redirect: ").strip()

access_token = api.exchange_code_for_access_token(code)
print "access token:\n", access_token
