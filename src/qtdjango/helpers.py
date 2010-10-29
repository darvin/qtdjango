from inspect import getmro
from qtdjango.models import User
#def get_registered_models(models):
#    ms =[]
#    for url, model in models.items():
#        model.resource_name = url
#        ms.append(model)
#    return ms
from qtdjango.connection import Connection


def get_resource_name_for_model(model):
    """docstring for get_resource_name_for_model"""
    app = model.__module__.split(".")[0]
    return app+r'/'+model.__name__.lower()+r's/' 


def get_all_models(app_list, from_django=False, exclude_model_names=("",)):
    """docstring for get_all_models"""
    models = []
    if from_django:
        from django.db.models import Model
        from django.contrib.auth.models import User
        model_base_class = Model
        user_class = User
    else:
        from models import Model
        from models import User
        model_base_class = Model
        user_class = User

    for app in app_list:
        m = __import__(".".join((app, "models")))
        module = getattr(m, "models")
        for name in dir(module):
            try:
                obj = getattr(module, name)
                if model_base_class in getmro(obj) and obj.__module__==app+".models" and \
                            obj.__name__ not in exclude_model_names:
                    if not from_django:
                        obj.resource_name = get_resource_name_for_model(obj)

                    models.append(obj)
            except AttributeError:
                pass

    models.append(user_class)
    user_class.resource_name=r"django/users/"
    return models

    
def test_connection(address, api_path, login, password):
    c = Connection(address, api_path, login, password)
    remote_version = c.get_resource_from_server("info")["qtdjango_version"]
    return remote_version
