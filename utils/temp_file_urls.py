import hmac
from hashlib import sha1
from time import time
method = 'GET'

def get_temp_url(self, path, ):
	duration_in_seconds = 60*60*24
	expires = int(time() + duration_in_seconds)
	path = '/v1/AUTH_a422b2-91f3-2f46-74b7-d7c9e8958f5d30/container/object'
	key = 'mykey'
	hmac_body = '%s\n%s\n%s' % (method, expires, path)
	sig = hmac.new(key, hmac_body, sha1).hexdigest()
	s = 'https://{host}/{path}?temp_url_sig={sig}&temp_url_expires={expires}'
	url = s.format(host='swift-cluster.example.com', path=path, sig=sig, expires=expires)