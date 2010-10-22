
from restclient.restful_lib import Connection
import json
import sys
import os
from helpers import get_all_models


class ModelsManager(object):
    """
    Models Manager class - loads models, save thems, etc...
    """

    def __init__(self, server, url, path_to_django_project, app_list, exclude_model_names=None,\
            login=None, password=None):
        """
        @param server: address of django server
        @param url: url path to django server api
        @param path_to_django: path to django project
        @param app_list: list of apps to process
        @param exclude_models: list to models which is not process
        @param login: login to django server
        @param password: password to django server
        """
        self.login, self.password, self.url = login, password, url
        self.__connection = Connection(server)
        self.models = self.__get_registered_models(path_to_django_project,\
                app_list, exclude_model_names)
        self.notify_dumped = []
        """@ivar notify_dumped: list of functions, that calls when all saved"""

        self.notify_undumped = []
        """@ivar notify_undumped: list of functions, that calls when changes"""


        for m in self.models:
            m.init_model_class(models_manager=self)
        for model in self.models:
            model.load()
        for model in self.models:
            model.refresh_foreing_keys()

    def add_notify_dumped(self, function):
        """
        Adds function to notify when models dumps list
        """
        self.notify_dumped.append(function)

    def add_notify_undumped(self, function):
        """
        Adds function to notify when models become have changes
        """
        self.notify_undumped.append(function)

    def notify_changes(self):
        """
        Notify changes in models
        """
        for func in self.notify_undumped:
            func()

    def dump(self):
        """
        Dump all models to server. Notify all functions about it
        """
        for model in self.models:
            model.dump()
        for func in self.notify_dumped:
            func()

    def is_all_dumped(self):
        """
        Returns True, if all models are dumped to server
        (if there is no unsaved changes)
        """
        for model in self.models:
            if not model.is_all_dumped():
                return False
        return True

    def get_resource_from_server(self, resource_name):
        """
        Gets responce from remote Django server
        @param resource_name: name of piston resource
        @rtype: dict
        """
        res = self.__connection.request_get("%s%s" % (self.url,resource_name))["body"]
        return json.loads(res)

    def post_resource_to_server(self, resource_name, args):
        """
        Posts to remote Django server
        @param resource_name: name of piston resource
        @param body: body of post request
        @rtype: dict
        """
        res = self.__connection.request_post("%s%s" % (self.url,resource_name),args=args)
        return res

    def do_models_magic_with_module(self, module):
        """
        Makes module automagicaly look like Django's models.py
        modules
        @param module: imported (via __import__()) module
        """
        for model in self.models:
            setattr(module, model.__name__, model)

    def __get_registered_models(self, path_to_django_project, app_list,
                              exclude_model_names=None):
        """
        Gets models from django project by parametres,
        @rtype: list of Models
        """
        if os.path.exists(path_to_django_project):
            path = path_to_django_project
        else:
            try:
                p = __import__(path_to_django_project)
                path = os.path.dirname(p.__file__)
            except ImportError:
                raise ImportError


        sys.path.append(path)

        ms = get_all_models(app_list, from_django=False,\
                            exclude_model_names=exclude_model_names)

        return ms



