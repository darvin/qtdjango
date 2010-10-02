from restclient.restful_lib import Connection
import json

ADDRESS = "http://127.0.0.1:8000"
API_PATH= "/api/"

class Connection(object):
    connection = Connection(ADDRESS)
    
    @classmethod
    def get(self, resname, **kwargs):
        res = self.connection.request_get("%s%s" % (API_PATH,resname))["body"]
        return json.loads(res)