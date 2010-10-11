'''
@author: darvin
This module must be imported from django enviroment
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.handler import BaseHandler
from helpers import get_resource_name_for_model, get_all_models



class CollectionHandler(BaseHandler):
    exclude = ()
    allowed_methods = ('GET',)

    def read(self, request,  *args, **kwargs):
        filterargs = {}
        for arg in request.GET:
            filterargs[arg] = request.GET[arg]

        return self.model.objects.filter(**filterargs) 


def get_url_pattens(app_list):
    """Gets app list returns urls patterns"""
    models = get_all_models(app_list, from_django=True)
    urlpatterns = [url(r"^"+get_resource_name_for_model(model),\
            Resource(type(model.__name__+"Handler", (CollectionHandler,), {"model":model})
                     )) for model in models]
 

    return patterns("", * urlpatterns)
    
    
    
