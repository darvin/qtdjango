from _socket import socket

__author__ = 'darvin'
import restclient.restful_lib
import json

class SocketError(Exception):
    pass
class ServerNotFoundError(Exception):
    pass

class NotQtDjangoResponceError(Exception):
    pass

class Connection(object):
    def __init__(self, server, url, login=None, password=None):
        self.login, self.password, self.url, self.server = login, password, url, server
        self.update_connection()

    def update_connection(self):
        self.__connection = restclient.restful_lib.Connection(self.server)

    def get_resource_from_server(self, resource_name):
        """
        Gets responce from remote Django server
        @param resource_name: name of piston resource
        @rtype: dict
        """
        try:
            res = self.__connection.request_get("%s%s" % (self.url,resource_name))["body"]
        except restclient.restful_lib.httplib2.socket.error:
            raise SocketError
        except restclient.httplib2.ServerNotFoundError:
            print "serv"
            raise ServerNotFoundError

        try:
            return json.loads(res)
        except ValueError:
            raise NotQtDjangoResponceError

    def post_resource_to_server(self, resource_name, args):
        """
        Posts to remote Django server
        @param resource_name: name of piston resource
        @param body: body of post request
        @rtype: dict
        """
        res = self.__connection.request_post("%s%s" % (self.url,resource_name),args=args)
        return res
