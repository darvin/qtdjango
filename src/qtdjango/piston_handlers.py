'''
@author: darvin
This module must be imported from django enviroment
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.handler import BaseHandler

from helpers import get_models_from_django_by_app


class CollectionHandler(BaseHandler):
    exclude = ()
    allowed_methods = ('GET',)
    
    def read(self, request,  *args, **kwargs):
        filterargs = {}
        for arg in request.GET:
            filterargs[arg] = request.GET[arg]

        return self.model.objects.filter(**filterargs) 

from django.contrib.auth.models import User

class UsersHandler(CollectionHandler):
    model=User
    
predefined_urlpatterns = [url(r"^django/users/", Resource(UsersHandler))]
def get_url_pattens(base_package, applist, include_models=None):
    urlpatterns = []
    for app in applist:
        models = get_models_from_django_by_app(base_package, app, include_models, true_django_model=True)
        
        handlers = [type(model.__name__+"Handler", (CollectionHandler,), {"model":model}) for model in models]
        urlpatterns_app = [url(r"^"+app+r"/"+handler.model.__name__.lower()+r"s/",
                   Resource(handler)) for handler in handlers]
        urlpatterns.extend(urlpatterns_app)

    return patterns("", * urlpatterns+predefined_urlpatterns)
    
    
    