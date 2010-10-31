


import sys
import os
import pickle
from helpers import get_all_models
from qtdjango.models import Model
from qtdjango.connection import Connection

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
        self.models = self.__get_registered_models(path_to_django_project,\
                app_list, exclude_model_names)



        self.notify_dumped = []
        """@ivar notify_dumped: list of functions, that calls when all saved"""

        self.notify_undumped = []
        """@ivar notify_undumped: list of functions, that calls when changes"""

        self.notify_user_changed = []

        self.models.sort(cmp=Model.is_model_depend_on)

        for m in self.models:
            m.version = 0
            m.init_model_class(models_manager=self)

        self.set_connection_params(server, url, login, password)


    def set_connection_params(self, server, url, login, password):

        self.__connection = Connection(server, url, login, password)
        current_user = self.get_current_user()
        for func in self.notify_user_changed:
            func(current_user)

    def load_from_server(self):
        try:
            for model in self.models:
                model.flush()
            for model in self.models:
                model.version += 1

                model.load()
            for model in self.models:
                model.refresh_foreing_keys()
            for model in self.models:
                model.notify()
        except:
            return False
        finally:
            for func in self.notify_dumped:
                func()
        return True

    def save_to_file(self, file):
        """
        Saves current modelmanager state to file
        """
        objs = {}
        for model in self.models:
            objs[model.__name__] = model.objects
        pickle.dump(objs, file)

    def load_from_file(self, file):
        """
        Loads modelmanager state from file
        """
        objs = pickle.load(file)

        for model in self.models:
            model.objects = objs[model.__name__]
            model.notify()
            print model.all()
        if not self.is_all_dumped():
            self.notify_changes()

        return True


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



    def add_notify_change_user(self, function):
        """
        Adds function to notify when models become have changes
        """
        self.notify_user_changed.append(function)


    def notify_changes(self):
        """
        Notify changes in models
        """
        for func in self.notify_undumped:
            func()

    def get_resource_from_server(self, resource_name):
        """
        Gets responce from remote Django server
        @param resource_name: name of piston resource
        @rtype: dict
        """
        return self.__connection.get_resource_from_server(resource_name)

    def post_resource_to_server(self, resource_name, args):
        """
        Posts to remote Django server
        @param resource_name: name of piston resource
        @param body: body of post request
        @rtype: dict
        """
        return self.__connection.post_resource_to_server(resource_name, args)



    def dump(self):
        """
        Dump all models to server. Notify all functions about it
        @return: responces dict of all models
        """
        responces = {}
        from operator import attrgetter

        self.models.sort(key=attrgetter("dump_order"))
        for model in self.models:
            print model
            responces[model.verbose_name(True)] = model.dump()
        for func in self.notify_dumped:
            func(responces)

    def is_all_dumped(self):
        """
        Returns True, if all models are dumped to server
        (if there is no unsaved changes)
        """
        for model in self.models:
            if not model.is_all_dumped():
                return False
        return True


    def do_models_magic_with_module(self, module):
        """
        Makes module automagicaly look like Django's models.py
        modules
        @param module: imported (via __import__()) module
        """
        for model in self.models:
            setattr(module, model.__name__, model)

    def __getattr__(self, name):
        try:
            return super(ModelsManager,self).__getattr__(name)
        except AttributeError:
            for model in self.models:
                if model.__name__==name:
                    return model
            raise AttributeError

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


    def get_current_user(self):
        user_name = self.__connection.get_login_password()[0]
        users = self.User.filter(username=user_name)
        if len(users)==1:
            return users[0]
        elif len(users)==0:
            return None
        else:
            raise AssertionError
