
from restful_lib import Connection, ConnectionError

# from gae_restful_lib import GAE_Connection

TINYURL_ENDPOINT = "http://tinyurl.com/api-create.php"
TINYURL_PARAM = "url"

class Tinyurl(object):
    def __init__(self):
        self._conn = Connection(TINYURL_ENDPOINT)
        # TODO test availability
        self.active = True
    
    def get(self, url):
        # Handcraft the ?url=XXX line as Tinyurl doesn't understand urlencoded
        # params - at least, when I try it anyway...
        response = self._conn.request_get("?%s=%s" % (TINYURL_PARAM, url))
        http_status = response['headers'].get('status')
        if http_status == "200":
            return response.get('body').encode('UTF-8')
        else:
            raise ConnectionError
