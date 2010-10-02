'''
@author: darvin
'''

from inspect import getmro

def get_models_from_django_by_app(base_package, app, include_models=None, true_django_model=False):
    
    models = []
    if true_django_model:
        from django.db.models import Model
        base_model_class = Model
    else:
        from qtdjango.models import Model
        base_model_class = Model
    
    thepackage = __import__(".".join((base_package, app, "models")))
    models_package = getattr(getattr(thepackage, app), "models")
    for modelname in dir(models_package):
        model = getattr(models_package, modelname)
        
        try:
            """We ensure, that base class of object is model (django or qtdjango),\
            and it is from current module"""
            if true_django_model:
                cond = model.__module__==app+".models"
            else:
                cond = model.__module__==base_package+"."+app+".models"
#            try:
#                print "###", model.__name__, model.__module__
#            except:
#                pass 
            if base_model_class in getmro(model) and cond:
                if include_models is not None:
                    if model.__name__ in include_models:
                        models.append(model)
                else:
                    models.append(model)
        except AttributeError:
            pass
    return models



def get_models_from_django(base_package, applist, include_models=None, true_django_model=False):
    models = []
    for app in applist:
        models.extend(get_models_from_django_by_app(base_package, app, include_models, true_django_model))
    return models

def get_registered_models_from_django(base_package, applist, include_models=None, true_django_model=False):
    models = []
    models_by_app = {}
    for app in applist:
        models_by_app[app]=get_models_from_django_by_app(base_package, app, include_models, true_django_model)
        models.extend(models_by_app[app])
    for model in models:
        model.load()
    return models
    

